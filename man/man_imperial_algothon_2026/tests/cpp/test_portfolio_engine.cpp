// Copyright 2026 Man Group Algothon Team. All rights reserved.
//
// test_portfolio_engine.cpp — Google Test suite for portfolio_engine.h
//
// Tests cover:
//   - EWCovEstimator: online update, annualisation, PD guarantee
//   - OAShrinkage: shrinkage coefficient validity
//   - RiskParityNewton: weight sum, ERC property
//   - MVOSolver: feasibility, simplex constraint

#include <gtest/gtest.h>
#include <Eigen/Dense>
#include <cmath>
#include <numeric>

#include "portfolio_engine.h"

using namespace algothon;

constexpr int kN = 10;
constexpr double kTol = 1e-6;

// ---------------------------------------------------------------------------
// Helper: random normal matrix
// ---------------------------------------------------------------------------
static Eigen::MatrixXd random_returns(int T, int N, unsigned seed = 42) {
  std::srand(seed);
  return Eigen::MatrixXd::Random(T, N) * 0.01;  // ~1% daily vol
}

// ---------------------------------------------------------------------------
// EWCovEstimator Tests
// ---------------------------------------------------------------------------

TEST(EWCovEstimator, CovarMatrixIsSymmetric) {
  EWCovEstimator<double> est(kN, 20.0);
  auto R = random_returns(200, kN);
  for (int t = 0; t < 200; ++t) {
    est.update(R.row(t).transpose());
  }
  auto C = est.get(false);
  EXPECT_TRUE(C.isApprox(C.transpose(), kTol));
}

TEST(EWCovEstimator, CovarMatrixIsPositiveDefinite) {
  EWCovEstimator<double> est(kN, 20.0);
  auto R = random_returns(200, kN);
  for (int t = 0; t < 200; ++t) {
    est.update(R.row(t).transpose());
  }
  auto C = est.get(true);
  Eigen::SelfAdjointEigenSolver<Eigen::MatrixXd> eig(C);
  EXPECT_GT(eig.eigenvalues().minCoeff(), 0.0);
}

TEST(EWCovEstimator, FeedRawMatchesFeedVector) {
  EWCovEstimator<double> est1(kN, 20.0);
  EWCovEstimator<double> est2(kN, 20.0);
  auto R = random_returns(100, kN);
  for (int t = 0; t < 100; ++t) {
    auto row = R.row(t).transpose().eval();
    est1.update(row);
    est2.update_raw(row.data());
  }
  auto C1 = est1.get(false);
  auto C2 = est2.get(false);
  EXPECT_TRUE(C1.isApprox(C2, kTol));
}

// ---------------------------------------------------------------------------
// OAShrinkage Tests
// ---------------------------------------------------------------------------

TEST(OAShrinkage, OutputIsSymmetric) {
  auto R  = random_returns(100, kN);
  auto S  = (R.transpose() * R) / 100.0 * 252.0;
  auto Cs = OAShrinkage<double>::apply(S, 100);
  EXPECT_TRUE(Cs.isApprox(Cs.transpose(), kTol));
}

TEST(OAShrinkage, DiagonalDominanceIncreases) {
  auto R  = random_returns(100, kN);
  auto S  = (R.transpose() * R) / 100.0 * 252.0;
  auto Cs = OAShrinkage<double>::apply(S, 100);
  // Shrinkage pulls toward identity → diagonal should increase or stay
  EXPECT_GE(Cs.diagonal().mean(), S.diagonal().mean() * 0.99);
}

// ---------------------------------------------------------------------------
// RiskParityNewton Tests
// ---------------------------------------------------------------------------

TEST(RiskParityNewton, WeightsSumToOne) {
  auto R  = random_returns(200, kN);
  auto S  = (R.transpose() * R) / 200.0 * 252.0;
  // Regularise
  S += 1e-4 * Eigen::MatrixXd::Identity(kN, kN);
  auto w = RiskParityNewton<double>::solve(S);
  EXPECT_NEAR(w.sum(), 1.0, kTol);
}

TEST(RiskParityNewton, AllWeightsPositive) {
  auto R  = random_returns(200, kN);
  auto S  = (R.transpose() * R) / 200.0 * 252.0;
  S += 1e-4 * Eigen::MatrixXd::Identity(kN, kN);
  auto w = RiskParityNewton<double>::solve(S);
  EXPECT_GT(w.minCoeff(), 0.0);
}

TEST(RiskParityNewton, EqualRiskContribution) {
  auto R  = random_returns(500, kN);
  auto S  = (R.transpose() * R) / 500.0 * 252.0;
  S += 1e-4 * Eigen::MatrixXd::Identity(kN, kN);
  auto w     = RiskParityNewton<double>::solve(S);
  double pv  = w.dot(S * w);
  Eigen::VectorXd rc = w.cwiseProduct(S * w) / pv;
  double target = 1.0 / kN;
  for (int i = 0; i < kN; ++i) {
    EXPECT_NEAR(rc(i), target, 1e-4);
  }
}

// ---------------------------------------------------------------------------
// MVOSolver Tests
// ---------------------------------------------------------------------------

TEST(MVOSolver, WeightsSumToOne) {
  auto R    = random_returns(200, kN);
  auto S    = (R.transpose() * R) / 200.0 * 252.0;
  S += 1e-4 * Eigen::MatrixXd::Identity(kN, kN);
  Eigen::VectorXd mu     = Eigen::VectorXd::Constant(kN, 0.05);
  Eigen::VectorXd w_prev = Eigen::VectorXd::Ones(kN) / kN;
  MVOSolver<double> solver(2.0, 0.001, 0.4);
  auto w = solver.solve(mu, S, w_prev);
  EXPECT_NEAR(w.sum(), 1.0, 1e-5);
}

TEST(MVOSolver, AllWeightsInBounds) {
  auto R    = random_returns(200, kN);
  auto S    = (R.transpose() * R) / 200.0 * 252.0;
  S += 1e-4 * Eigen::MatrixXd::Identity(kN, kN);
  Eigen::VectorXd mu     = Eigen::VectorXd::Constant(kN, 0.05);
  Eigen::VectorXd w_prev = Eigen::VectorXd::Ones(kN) / kN;
  MVOSolver<double> solver(2.0, 0.001, 0.4);
  auto w = solver.solve(mu, S, w_prev);
  EXPECT_GE(w.minCoeff(), -1e-6);
  EXPECT_LE(w.maxCoeff(), 0.4 + 1e-6);
}

// ---------------------------------------------------------------------------
// PortfolioEngine Integration Test
// ---------------------------------------------------------------------------

TEST(PortfolioEngine, EndToEnd) {
  PortfolioEngine eng(kN, 2.0, 0.001, 30.0);
  auto R = random_returns(300, kN);
  for (int t = 0; t < 300; ++t) {
    eng.feed_returns(R.row(t).data());
  }
  std::vector<double> mu(kN, 0.05), w_prev(kN, 1.0 / kN), w_out(kN);
  eng.optimize(mu.data(), w_prev.data(), w_out.data());

  double sum = std::accumulate(w_out.begin(), w_out.end(), 0.0);
  EXPECT_NEAR(sum, 1.0, 1e-5);
  for (double wi : w_out) EXPECT_GE(wi, -1e-6);
}
