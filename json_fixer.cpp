#include <SSVUtilsJson/SSVUtilsJson.h>
#include <SSVJsonCpp/SSVJsonCpp.h>
#include <pybind11/pybind11.h>
#include <iostream>
#include <fstream>


std::string fix_json(std::string file) {
    Json::Value root = ssvuj::getRootFromFile(file);
    Json::FastWriter fastwriter;
    return fastwriter.write(root);
}

PYBIND11_MODULE(json_fixer, m) {
    m.def("fix_json", &fix_json, "A function that reads a JSON file in a very lenient way");
}
