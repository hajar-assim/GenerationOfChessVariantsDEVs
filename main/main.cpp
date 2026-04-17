// chess variant cell-devs simulation driver
// supports both the original fixed-threshold model and the adaptive density-based model
// reads a json config and runs the simulation with csv logging
// usage: ./chess_variant <config.json> [sim_time]

#include "nlohmann/json.hpp"
#include <cadmium/modeling/celldevs/grid/coupled.hpp>
#include <cadmium/simulation/logger/csv.hpp>
#include <cadmium/simulation/root_coordinator.hpp>
#include <chrono>
#include <fstream>
#include <iostream>
#include <string>
#include <filesystem>
#include "include/chessVariantCell.hpp"
#include "include/adaptiveChessVariantCell.hpp"

using namespace cadmium::celldevs;
using namespace cadmium;

// factory for original fixed-threshold cells
std::shared_ptr<GridCell<ChessVariantState, double>> addFixedGridCell(
    const coordinates& cellId,
    const std::shared_ptr<const GridCellConfig<ChessVariantState, double>>& cellConfig) {
    auto cellModel = cellConfig->cellModel;
    if (cellModel == "chessVariant") {
        return std::make_shared<ChessVariantCell>(cellId, cellConfig);
    } else {
        throw std::bad_typeid();
    }
}

// factory for adaptive density-based cells
std::shared_ptr<GridCell<AdaptiveChessVariantState, double>> addAdaptiveGridCell(
    const coordinates& cellId,
    const std::shared_ptr<const GridCellConfig<AdaptiveChessVariantState, double>>& cellConfig) {
    auto cellModel = cellConfig->cellModel;
    if (cellModel == "adaptiveChessVariant") {
        return std::make_shared<AdaptiveChessVariantCell>(cellId, cellConfig);
    } else {
        throw std::bad_typeid();
    }
}

// detect which model type the config uses by reading the default cell model field
std::string detectModelType(const std::string& configFilePath) {
    std::ifstream f(configFilePath);
    nlohmann::json config = nlohmann::json::parse(f);
    return config["cells"]["default"]["model"].get<std::string>();
}

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cout << "Program used with wrong parameters. The program must be invoked as follows:" << std::endl;
        std::cout << argv[0] << " SCENARIO_CONFIG.json [MAX_SIMULATION_TIME (default: 500)]" << std::endl;
        return -1;
    }

    std::string configFilePath = argv[1];
    double simTime = (argc > 2) ? std::stod(argv[2]) : 500;

    // output goes to logs/<config_name>_grid_log.csv
    std::filesystem::create_directories("logs");
    std::string configName = std::filesystem::path(configFilePath).stem().string();
    std::string baseName = configName;
    if (baseName.size() > 7 && baseName.substr(baseName.size() - 7) == "_config") {
        baseName = baseName.substr(0, baseName.size() - 7);
    }
    std::string logFile = "logs/" + baseName + "_grid_log.csv";

    std::string modelType = detectModelType(configFilePath);
    std::cout << "Detected model type: " << modelType << std::endl;

    if (modelType == "adaptiveChessVariant") {
        // adaptive density-based model
        auto model = std::make_shared<GridCellDEVSCoupled<AdaptiveChessVariantState, double>>(
            "adaptiveChessVariant", addAdaptiveGridCell, configFilePath);
        model->buildModel();

        auto rootCoordinator = RootCoordinator(model);
        rootCoordinator.setLogger<CSVLogger>(logFile, ";");

        rootCoordinator.start();
        rootCoordinator.simulate(simTime);
        rootCoordinator.stop();
    } else {
        // original fixed-threshold model
        auto model = std::make_shared<GridCellDEVSCoupled<ChessVariantState, double>>(
            "chessVariant", addFixedGridCell, configFilePath);
        model->buildModel();

        auto rootCoordinator = RootCoordinator(model);
        rootCoordinator.setLogger<CSVLogger>(logFile, ";");

        rootCoordinator.start();
        rootCoordinator.simulate(simTime);
        rootCoordinator.stop();
    }

    std::cout << "Simulation complete. Output: " << logFile << std::endl;
}
