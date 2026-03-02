#ifndef TWO_SIGMA_DATA_GENERATOR_H
#define TWO_SIGMA_DATA_GENERATOR_H

#include <string>

namespace two_sigma {

class DataGenerator {
public:
    DataGenerator(int n_samples = 1000, int n_features = 100, int n_instruments = 50);
    void generate(const std::string& output_path);

private:
    int n_samples_;
    int n_features_;
    int n_instruments_;
};

} // namespace two_sigma

#endif // TWO_SIGMA_DATA_GENERATOR_H
