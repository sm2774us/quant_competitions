// Copyright 2026 Man Group Algothon Team. All rights reserved.
//
// bindings.cpp — nanobind Python ↔ C++26 bridge
//
// Exposes the high-performance algothon::PortfolioEngine and its constituent
// solvers to Python via nanobind.  NumPy arrays are bound zero-copy using
// nanobind's ndarray support.
//
// Usage (Python):
//   import algothon_cpp as cpp
//
//   eng = cpp.PortfolioEngine(n_assets=10, risk_aversion=2.0)
//   for row in returns_matrix:
//       eng.feed_returns(row)
//   weights = eng.optimize(mu, w_prev)
//   rp_weights = eng.risk_parity()

#include <nanobind/nanobind.h>
#include <nanobind/ndarray.h>
#include <nanobind/stl/string.h>
#include <nanobind/stl/vector.h>

#include <stdexcept>
#include <string>
#include <vector>

#include "portfolio_engine.h"

namespace nb = nanobind;
using namespace algothon;

// Convenience type alias for 1-D and 2-D double numpy arrays
using Array1D = nb::ndarray<double, nb::ndim<1>, nb::c_contig, nb::device::cpu>;
using Array2D = nb::ndarray<double, nb::ndim<2>, nb::c_contig, nb::device::cpu>;

// ---------------------------------------------------------------------------
// Helper: validate array length matches expected
// ---------------------------------------------------------------------------
static void check_size(const Array1D& arr, int expected, const std::string& name) {
  if (static_cast<int>(arr.shape(0)) != expected) {
    throw std::invalid_argument(
        name + ": expected " + std::to_string(expected) +
        " elements, got " + std::to_string(arr.shape(0)));
  }
}

// ---------------------------------------------------------------------------
// Python-friendly wrapper around PortfolioEngine
// ---------------------------------------------------------------------------
struct PyPortfolioEngine {
  explicit PyPortfolioEngine(int n_assets, double risk_aversion,
                             double tc_penalty, double ewm_halflife)
      : engine_(n_assets, risk_aversion, tc_penalty, ewm_halflife),
        n_(n_assets) {}

  /// Feed a 1-D numpy array of returns into the covariance estimator.
  void feed_returns(Array1D returns) {
    check_size(returns, n_, "returns");
    engine_.feed_returns(returns.data());
  }

  /// Feed an entire 2-D returns matrix (T x N) in one call.
  void feed_returns_matrix(Array2D matrix) {
    if (static_cast<int>(matrix.shape(1)) != n_)
      throw std::invalid_argument("feed_returns_matrix: expected " +
                                  std::to_string(n_) + " columns");
    const int T = static_cast<int>(matrix.shape(0));
    const double* ptr = matrix.data();
    for (int t = 0; t < T; ++t) {
      engine_.feed_returns(ptr + t * n_);
    }
  }

  /// Compute optimal MVO weights.
  /// Returns a new numpy array of shape (n_assets,).
  nb::ndarray<nb::numpy, double, nb::ndim<1>> optimize(Array1D mu, Array1D w_prev) {
    check_size(mu, n_, "mu");
    check_size(w_prev, n_, "w_prev");

    // Allocate output
    auto* data = new double[n_];
    engine_.optimize(mu.data(), w_prev.data(), data);

    nb::capsule deleter(data, [](void* p) noexcept {
      delete[] static_cast<double*>(p);
    });
    size_t shape[1] = {static_cast<size_t>(n_)};
    return nb::ndarray<nb::numpy, double, nb::ndim<1>>(data, 1, shape, deleter);
  }

  /// Compute risk-parity weights.
  nb::ndarray<nb::numpy, double, nb::ndim<1>> risk_parity() {
    auto* data = new double[n_];
    engine_.risk_parity(data);
    nb::capsule deleter(data, [](void* p) noexcept {
      delete[] static_cast<double*>(p);
    });
    size_t shape[1] = {static_cast<size_t>(n_)};
    return nb::ndarray<nb::numpy, double, nb::ndim<1>>(data, 1, shape, deleter);
  }

  void reset() { engine_.reset(); }
  int n_assets() const { return n_; }

 private:
  PortfolioEngine engine_;
  int             n_;
};

// ---------------------------------------------------------------------------
// Module definition
// ---------------------------------------------------------------------------

NB_MODULE(algothon_cpp, m) {
  m.doc() = R"(
algothon_cpp — High-performance portfolio construction library.

Provides SIMD-accelerated (Eigen) implementations of:
  - Exponentially-weighted covariance estimation (OAS-shrunk)
  - Markowitz MVO via projected Barzilai-Borwein gradient descent
  - Risk-parity via Newton-Raphson

All array operations are zero-copy with NumPy via nanobind.
)";

  nb::class_<PyPortfolioEngine>(m, "PortfolioEngine")
      .def(nb::init<int, double, double, double>(),
           nb::arg("n_assets")      = 10,
           nb::arg("risk_aversion") = 2.0,
           nb::arg("tc_penalty")    = 0.001,
           nb::arg("ewm_halflife")  = 30.0,
           R"(
Construct a PortfolioEngine.

Args:
    n_assets:      Number of instruments.
    risk_aversion: MVO lambda (higher = more risk-averse).
    tc_penalty:    Transaction cost L1 penalty coefficient.
    ewm_halflife:  EWM covariance half-life in trading days.
)")
      .def("feed_returns", &PyPortfolioEngine::feed_returns,
           nb::arg("returns"),
           "Feed a 1-D numpy return vector into the covariance estimator.")
      .def("feed_returns_matrix", &PyPortfolioEngine::feed_returns_matrix,
           nb::arg("matrix"),
           "Feed a 2-D (T x N) returns matrix into the covariance estimator.")
      .def("optimize", &PyPortfolioEngine::optimize,
           nb::arg("mu"), nb::arg("w_prev"),
           R"(
Compute optimal MVO weights.

Args:
    mu:     (N,) expected return vector.
    w_prev: (N,) previous period weights for TC penalisation.

Returns:
    (N,) numpy array of optimal weights summing to 1.
)")
      .def("risk_parity", &PyPortfolioEngine::risk_parity,
           R"(
Compute equal-risk-contribution (risk-parity) weights.

Returns:
    (N,) numpy array of risk-parity weights summing to 1.
)")
      .def("reset", &PyPortfolioEngine::reset,
           "Reset the internal covariance estimator state.")
      .def_prop_ro("n_assets", &PyPortfolioEngine::n_assets,
                   "Number of assets in the portfolio.");
}
