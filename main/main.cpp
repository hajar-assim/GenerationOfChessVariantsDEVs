// chess variant cell-devs simulation driver
// supports both the original fixed-threshold model and the adaptive density-based model
// reads a json config and runs the simulation with csv logging
// usage: ./chess_variant <config.json> [sim_time]

#include "nlohmann/json.hpp"
#include <cadmium/modeling/celldevs/grid/coupled.hpp>
#include <cadmium/modeling/celldevs/asymm/coupled.hpp>
#include <cadmium/simulation/logger/csv.hpp>
#include <cadmium/simulation/root_coordinator.hpp>
#include <chrono>
#include <fstream>
#include <iostream>
#include <string>
#include <filesystem>
#include "include/chessVariantCell.hpp"
#include "include/adaptiveChessVariantCell.hpp"
#include "include/asymmChessVariantCell.hpp"
#include "include/boardControlCell.hpp"
#include "include/lifecycleChessVariantCell.hpp"
#include "include/losChessVariantCell.hpp"
#include "include/propagationChessVariantCell.hpp"

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

// factory for asymmetric rule-zone cells
std::shared_ptr<AsymmCell<AdaptiveChessVariantState, double>> addAsymmChessVariantCell(
    const std::string& cellId,
    const std::shared_ptr<const AsymmCellConfig<AdaptiveChessVariantState, double>>& cellConfig) {
    auto cellModel = cellConfig->cellModel;
    if (cellModel == "asymmChessVariant") {
        return std::make_shared<AsymmChessVariantCell>(cellId, cellConfig);
    } else {
        throw std::bad_typeid();
    }
}

// factory for board control influence analysis cells
std::shared_ptr<GridCell<BoardControlState, double>> addBoardControlCell(
    const coordinates& cellId,
    const std::shared_ptr<const GridCellConfig<BoardControlState, double>>& cellConfig) {
    auto cellModel = cellConfig->cellModel;
    if (cellModel == "boardControl") {
        return std::make_shared<BoardControlCell>(cellId, cellConfig);
    } else {
        throw std::bad_typeid();
    }
}

// factory for lifecycle continuous-activity cells
std::shared_ptr<GridCell<LifecycleChessVariantState, double>> addLifecycleGridCell(
    const coordinates& cellId,
    const std::shared_ptr<const GridCellConfig<LifecycleChessVariantState, double>>& cellConfig) {
    auto cellModel = cellConfig->cellModel;
    if (cellModel == "lifecycleChessVariant") {
        return std::make_shared<LifecycleChessVariantCell>(cellId, cellConfig);
    } else {
        throw std::bad_typeid();
    }
}

// factory for propagation influence cells
std::shared_ptr<GridCell<PropagationChessVariantState, double>> addPropagationGridCell(
    const coordinates& cellId,
    const std::shared_ptr<const GridCellConfig<PropagationChessVariantState, double>>& cellConfig) {
    auto cellModel = cellConfig->cellModel;
    if (cellModel == "propagationChessVariant") {
        return std::make_shared<PropagationChessVariantCell>(cellId, cellConfig);
    } else {
        throw std::bad_typeid();
    }
}

// factory for line-of-sight blocking cells
std::shared_ptr<GridCell<AdaptiveChessVariantState, double>> addLOSGridCell(
    const coordinates& cellId,
    const std::shared_ptr<const GridCellConfig<AdaptiveChessVariantState, double>>& cellConfig) {
    auto cellModel = cellConfig->cellModel;
    if (cellModel == "losChessVariant") {
        return std::make_shared<LOSChessVariantCell>(cellId, cellConfig);
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

    // output goes to logs/<subdir>/<config_name>_grid_log.csv
    // mirrors the config directory structure (e.g. config/los/ -> logs/los/)
    std::filesystem::path configPath(configFilePath);
    std::string configName = configPath.stem().string();
    std::string baseName = configName;
    if (baseName.size() > 7 && baseName.substr(baseName.size() - 7) == "_config") {
        baseName = baseName.substr(0, baseName.size() - 7);
    }

    // extract subdirectory from config path (e.g. "config/los/file.json" -> "los")
    std::string logSubdir = "";
    auto parentDir = configPath.parent_path().filename().string();
    if (parentDir != "config" && parentDir != "." && parentDir != "") {
        logSubdir = parentDir + "/";
    }
    std::string logDir = "logs/" + logSubdir;
    std::filesystem::create_directories(logDir);
    std::string logFile = logDir + baseName + "_grid_log.csv";

    std::string modelType = detectModelType(configFilePath);
    std::cout << "Detected model type: " << modelType << std::endl;

    if (modelType == "propagationChessVariant") {
        // propagation influence model
        auto model = std::make_shared<GridCellDEVSCoupled<PropagationChessVariantState, double>>(
            "propagationChessVariant", addPropagationGridCell, configFilePath);
        model->buildModel();

        auto rootCoordinator = RootCoordinator(model);
        rootCoordinator.setLogger<CSVLogger>(logFile, ";");

        rootCoordinator.start();
        rootCoordinator.simulate(simTime);
        rootCoordinator.stop();
    } else if (modelType == "lifecycleChessVariant") {
        // lifecycle continuous-activity model
        auto model = std::make_shared<GridCellDEVSCoupled<LifecycleChessVariantState, double>>(
            "lifecycleChessVariant", addLifecycleGridCell, configFilePath);
        model->buildModel();

        auto rootCoordinator = RootCoordinator(model);
        rootCoordinator.setLogger<CSVLogger>(logFile, ";");

        rootCoordinator.start();
        rootCoordinator.simulate(simTime);
        rootCoordinator.stop();
    } else if (modelType == "losChessVariant") {
        // line-of-sight blocking model (uses same state as adaptive)
        auto model = std::make_shared<GridCellDEVSCoupled<AdaptiveChessVariantState, double>>(
            "losChessVariant", addLOSGridCell, configFilePath);
        model->buildModel();

        auto rootCoordinator = RootCoordinator(model);
        rootCoordinator.setLogger<CSVLogger>(logFile, ";");

        rootCoordinator.start();
        rootCoordinator.simulate(simTime);
        rootCoordinator.stop();
    } else if (modelType == "boardControl") {
        // board control influence analysis model
        auto model = std::make_shared<GridCellDEVSCoupled<BoardControlState, double>>(
            "boardControl", addBoardControlCell, configFilePath);
        model->buildModel();

        auto rootCoordinator = RootCoordinator(model);
        rootCoordinator.setLogger<CSVLogger>(logFile, ";");

        rootCoordinator.start();
        rootCoordinator.simulate(simTime);
        rootCoordinator.stop();
    } else if (modelType == "asymmChessVariant") {
        // asymmetric rule-zone model - per-cell rule parameterization
        auto model = std::make_shared<AsymmCellDEVSCoupled<AdaptiveChessVariantState, double>>(
            "asymmChessVariant", addAsymmChessVariantCell, configFilePath);
        model->buildModel();

        auto rootCoordinator = RootCoordinator(model);
        rootCoordinator.setLogger<CSVLogger>(logFile, ";");

        rootCoordinator.start();
        rootCoordinator.simulate(simTime);
        rootCoordinator.stop();
    } else if (modelType == "adaptiveChessVariant") {
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
