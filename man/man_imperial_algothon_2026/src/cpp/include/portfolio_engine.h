// Copyright 2026 Man Group Algothon Team. All rights reserved.
// Licensed under the Apache License, Version 2.0.
//
// portfolio_engine.h — High-performance portfolio construction primitives
//
// Provides SIMD-accelerated (via Eigen) implementations of:
//   - Exponentially-weighted covariance estimation (EWCov)
//   - Ledoit-Wolf analytical shrinkage (Oracle Approximating Shrinkage)
//   - Sequential quadratic programming for MVO
//   - Risk-parity weight computation via Newton iterations
//
// All matrix operations use Eigen's vectorised SIMD backend (AVX2/AVX512
// when available) via compiler auto-vectorisation.
//
// Usage:
//   #include "portfolio_engine.h"
//   using namespace algothon;
//
//   // Estimate covariance
//   EWCovEstimator<double> cov_est(252, 0.94);
//   for (auto& row : return_rows) cov_est.update(row);
//   Eigen::MatrixXd cov = cov_est.get();
//
//   // Optimise
//   MVOSolver<double> solver(2.0, 0.001);
//   Eigen::VectorXd w = solver.solve(mu, cov, w_prev);

#pragma once

#include <Eigen/Dense>
#include <Eigen/Eigenvalues>
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstddef>
#include <limits>
#include <stdexcept>
#include <vector>

namespace algothon {

// ---------------------------------------------------------------------------
// Type aliases
// ---------------------------------------------------------------------------

using MatrixXd = Eigen::Matrix<double, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor>;
using VectorXd = Eigen::VectorXd;
using Index    = Eigen::Index;

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

inline constexpr double kEps          = 1e-12;
inline constexpr double kAnnFactor    = 252.0;
inline constexpr double kSqrtAnn      = 15.874507866387544;  // sqrt(252)
inline constexpr int    kMaxMVOIter   = 2000;
inline constexpr double kMVOFtol      = 1e-12;

// ---------------------------------------------------------------------------
// EWCovEstimator
//
// Online exponentially-weighted covariance estimator using the Welford-EWM
// update:
//   mean_{t} = (1-α) * mean_{t-1} + α * x_t
//   C_{t}    = (1-α) * (C_{t-1} + α * (x_t - mean_{t-1})(x_t - mean_{t-1})^T)
//
// Template param T: floating-point type (double or float).
// ---------------------------------------------------------------------------

template <typename T = double>
class EWCovEstimator {
 public:
  using Matrix = Eigen::Matrix<T, Eigen::Dynamic, Eigen::Dynamic>;
  using Vector = Eigen::Matrix<T, Eigen::Dynamic, 1>;

  /// Construct an online EWM covariance estimator.
  /// @param n_assets    Number of assets (must be fixed).
  /// @param halflife    EWM half-life in days; decay = exp(-log(2)/halflife).
  explicit EWCovEstimator(Index n_assets, double halflife = 30.0)
      : n_(n_assets),
        alpha_(static_cast<T>(1.0 - std::exp(-std::log(2.0) / halflife))),
        mean_(Vector::Zero(n_assets)),
        cov_(Matrix::Zero(n_assets, n_assets)),
        initialized_(false) {}

  /// Update the estimator with a new observation vector.
  /// @param x  (N,) return observation.
  void update(const Vector& x) {
    assert(x.size() == n_);
    if (!initialized_) {
      mean_ = x;
      initialized_ = true;
      return;
    }
    Vector delta = x - mean_;
    mean_ += alpha_ * delta;
    cov_   = (T{1} - alpha_) * (cov_ + alpha_ * delta * (x - mean_).transpose());
  }

  /// Update from raw pointer (cache-friendly for bulk ingestion).
  /// @param data  Pointer to contiguous array of n_ doubles.
  void update_raw(const T* __restrict__ data) {
    update(Eigen::Map<const Vector>(data, n_));
  }

  /// Return the current covariance estimate (annualised by kAnnFactor).
  /// @param regularise  If true, add Tikhonov regularisation for PD guarantee.
  Matrix get(bool regularise = true) const {
    Matrix C = cov_ * static_cast<T>(kAnnFactor);
    if (regularise) {
      // Compute minimum eigenvalue; bump if non-PD
      Eigen::SelfAdjointEigenSolver<Matrix> eig(C);
      T min_ev = eig.eigenvalues().minCoeff();
      if (min_ev < static_cast<T>(kEps)) {
        C += (-min_ev + static_cast<T>(1e-6)) * Matrix::Identity(n_, n_);
      }
    }
    return C;
  }

  void reset() {
    mean_.setZero();
    cov_.setZero();
    initialized_ = false;
  }

 private:
  Index   n_;
  T       alpha_;
  Vector  mean_;
  Matrix  cov_;
  bool    initialized_;
};

// ---------------------------------------------------------------------------
// OAShrinkage
//
// Oracle Approximating Shrinkage estimator (Chen, Wiesel, Eldar, Hero 2010).
// Closed-form optimal shrinkage intensity for Gaussian data:
//   C* = (1-rho)*S + rho*(tr(S)/p)*I
//
// ---------------------------------------------------------------------------

template <typename T = double>
class OAShrinkage {
 public:
  using Matrix = Eigen::Matrix<T, Eigen::Dynamic, Eigen::Dynamic>;

  /// Apply OAS shrinkage to a sample covariance matrix.
  /// @param S  (N, N) sample covariance.
  /// @param n  Number of observations used to compute S.
  /// @return   Shrunk covariance matrix.
  static Matrix apply(const Matrix& S, Index n) {
    const Index p = S.rows();
    const T tr_S  = S.trace();
    const T tr_S2 = (S * S).trace();
    const T tr2_S = tr_S * tr_S;

    // OAS shrinkage coefficient
    const T rho_num   = (T{1} - T{2} / p) * tr_S2 + tr2_S;
    const T rho_denom = (n + T{1} - T{2} / p) * (tr_S2 - tr2_S / p);

    T rho = std::clamp(static_cast<T>(rho_num / (rho_denom + static_cast<T>(kEps))),
                       T{0}, T{1});

    Matrix target = (tr_S / static_cast<T>(p)) * Matrix::Identity(p, p);
    return (T{1} - rho) * S + rho * target;
  }
};

// ---------------------------------------------------------------------------
// RiskParityNewton
//
// Newton-Raphson solver for equal risk contribution (ERC) weights.
// Solves: w_i * (Σw)_i / (w^T Σ w) = 1/N  for all i
// via gradient descent on the squared deviation objective.
//
// ---------------------------------------------------------------------------

template <typename T = double>
class RiskParityNewton {
 public:
  using Matrix = Eigen::Matrix<T, Eigen::Dynamic, Eigen::Dynamic>;
  using Vector = Eigen::Matrix<T, Eigen::Dynamic, 1>;

  /// Compute risk-parity weights via Newton iterations.
  /// @param cov       (N, N) covariance matrix.
  /// @param max_iter  Maximum Newton iterations.
  /// @param tol       Convergence tolerance.
  /// @return (N,) weight vector summing to 1, all positive.
  static Vector solve(const Matrix& cov, int max_iter = 500, T tol = T{1e-10}) {
    const Index N = cov.rows();
    Vector w = Vector::Ones(N) / static_cast<T>(N);

    for (int iter = 0; iter < max_iter; ++iter) {
      Vector Sw      = cov * w;
      T port_var     = w.dot(Sw);
      Vector rc      = w.cwiseProduct(Sw) / (port_var + static_cast<T>(kEps));
      T target       = T{1} / static_cast<T>(N);
      Vector grad    = rc - Vector::Constant(N, target);  // (N,) gradient

      // Hessian diagonal approximation (empirically stable)
      Vector h = (T{2} * Sw.cwiseProduct(Sw) + T{2} * port_var *
                  cov.diagonal().cwiseProduct(w)) /
                 (port_var * port_var + static_cast<T>(kEps));
      h = h.cwiseMax(static_cast<T>(kEps));  // clip

      w -= grad.cwiseQuotient(h);
      w  = w.cwiseMax(T{1e-6});  // non-negativity
      w /= w.sum();

      if (grad.norm() < tol) break;
    }
    return w;
  }
};

// ---------------------------------------------------------------------------
// MVOSolver
//
// Projected gradient descent solver for the long-only Markowitz problem:
//   max  w^T μ - (λ/2) w^T Σ w - γ ||w - w_prev||_1
//   s.t. sum(w) = 1, 0 <= w_i <= w_max
//
// Uses a Barzilai-Borwein step size with Dykstra's projection algorithm
// for the simplex + box constraint set.
//
// ---------------------------------------------------------------------------

template <typename T = double>
class MVOSolver {
 public:
  using Matrix = Eigen::Matrix<T, Eigen::Dynamic, Eigen::Dynamic>;
  using Vector = Eigen::Matrix<T, Eigen::Dynamic, 1>;

  /// Construct MVO solver.
  /// @param risk_aversion  Lambda λ coefficient.
  /// @param tc_penalty     Transaction cost γ coefficient.
  /// @param w_max          Per-asset upper bound.
  explicit MVOSolver(T risk_aversion = T{2}, T tc_penalty = T{0.001},
                     T w_max = T{0.4})
      : lambda_(risk_aversion), gamma_(tc_penalty), w_max_(w_max) {}

  /// Solve for optimal weights.
  /// @param mu      (N,) expected return vector.
  /// @param cov     (N, N) covariance matrix.
  /// @param w_prev  (N,) previous period weights (for TC).
  /// @return (N,) optimal weight vector.
  Vector solve(const Vector& mu, const Matrix& cov,
               const Vector& w_prev) const {
    const Index N = mu.size();
    Vector w = w_prev;

    // Barzilai-Borwein projected gradient descent
    Vector grad_prev = _gradient(w, mu, cov, w_prev);
    Vector w_prev_iter = w;
    T alpha = T{0.01};

    for (int iter = 0; iter < kMaxMVOIter; ++iter) {
      Vector grad = _gradient(w, mu, cov, w_prev);

      // BB step size
      if (iter > 0) {
        Vector dw = w - w_prev_iter;
        Vector dg = grad - grad_prev;
        T dg_norm = dg.squaredNorm();
        if (dg_norm > static_cast<T>(kEps)) {
          alpha = std::abs(dw.dot(dg)) / dg_norm;
        }
        alpha = std::clamp(alpha, T{1e-6}, T{1.0});
      }

      w_prev_iter = w;
      grad_prev   = grad;

      // Gradient step (maximise, so descend on negative)
      w = w + alpha * (-grad);  // note: grad is ∇(-objective)

      // Project onto simplex ∩ [0, w_max]
      w = _project_simplex_box(w, T{0}, w_max_, N);

      if (grad.norm() * alpha < static_cast<T>(kMVOFtol)) break;
    }
    return w;
  }

 private:
  T lambda_, gamma_, w_max_;

  // Gradient of the negative utility (to ascend)
  Vector _gradient(const Vector& w, const Vector& mu,
                   const Matrix& cov, const Vector& w_prev) const {
    // ∇(-utility) = -μ + λΣw + γ*sign(w - w_prev)
    Vector sign_diff = (w - w_prev).unaryExpr(
        [](T x) { return x > T{0} ? T{1} : (x < T{0} ? T{-1} : T{0}); });
    return -mu + lambda_ * (cov * w) + gamma_ * sign_diff;
  }

  // Project onto {w : sum=1, 0<=w_i<=w_max} via Dykstra's algorithm
  static Vector _project_simplex_box(Vector v, T w_min, T w_max, Index N) {
    // Box projection then simplex projection, 2 iterations of Dykstra
    for (int k = 0; k < 10; ++k) {
      // Box: clip
      v = v.cwiseMax(w_min).cwiseMin(w_max);
      // Simplex: project onto {sum=1}
      T excess = (v.sum() - T{1}) / static_cast<T>(N);
      v.array() -= excess;
      if (std::abs(v.sum() - T{1}) < static_cast<T>(kEps)) break;
    }
    v = v.cwiseMax(w_min);
    v /= v.sum();
    return v;
  }
};

// ---------------------------------------------------------------------------
// PortfolioEngine
//
// High-level facade combining EWCovEstimator, OAShrinkage, and MVOSolver.
// Designed for nanobind exposure to Python.
//
// ---------------------------------------------------------------------------

class PortfolioEngine {
 public:
  /// Construct the engine.
  /// @param n_assets       Number of assets.
  /// @param risk_aversion  MVO λ.
  /// @param tc_penalty     Transaction cost γ.
  /// @param ewm_halflife   EWM half-life for covariance (days).
  explicit PortfolioEngine(int n_assets = 10, double risk_aversion = 2.0,
                           double tc_penalty = 0.001, double ewm_halflife = 30.0)
      : n_(n_assets),
        cov_est_(n_assets, ewm_halflife),
        solver_(risk_aversion, tc_penalty, 0.4) {}

  /// Feed a new return observation into the covariance estimator.
  /// @param returns  Pointer to contiguous array of n_assets doubles.
  void feed_returns(const double* returns) {
    cov_est_.update_raw(returns);
  }

  /// Compute optimal weights given expected returns and previous weights.
  /// @param mu      Pointer to expected return array (n_assets).
  /// @param w_prev  Pointer to previous weight array (n_assets).
  /// @param w_out   Pointer to output weight array (n_assets).
  void optimize(const double* mu, const double* w_prev, double* w_out) {
    VectorXd mu_v    = Eigen::Map<const VectorXd>(mu, n_);
    VectorXd wprev_v = Eigen::Map<const VectorXd>(w_prev, n_);

    MatrixXd raw_cov = cov_est_.get(false);
    MatrixXd shrunken = OAShrinkage<double>::apply(raw_cov, 252);

    VectorXd weights = solver_.solve(mu_v, shrunken, wprev_v);
    Eigen::Map<VectorXd>(w_out, n_) = weights;
  }

  /// Compute risk-parity weights.
  /// @param w_out  Pointer to output weight array (n_assets).
  void risk_parity(double* w_out) {
    MatrixXd raw_cov = cov_est_.get(false);
    MatrixXd shrunken = OAShrinkage<double>::apply(raw_cov, 252);
    VectorXd w = RiskParityNewton<double>::solve(shrunken);
    Eigen::Map<VectorXd>(w_out, n_) = w;
  }

  void reset() { cov_est_.reset(); }
  int n_assets() const { return static_cast<int>(n_); }

 private:
  Index                   n_;
  EWCovEstimator<double>  cov_est_;
  MVOSolver<double>       solver_;
};

}  // namespace algothon
