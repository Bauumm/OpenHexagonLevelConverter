#include <SSVUtilsJson/SSVUtilsJson.h>
#include <SSVJsonCpp/SSVJsonCpp.h>
#include <pybind11/pybind11.h>
#include <iostream>
#include <fstream>


std::string fix_json_file(std::string file) {
    Json::Value root = ssvuj::getRootFromFile(file);
    Json::FastWriter fastwriter;
    return fastwriter.write(root);
}

std::string fix_json_string(std::string string) {
    Json::Value root = ssvuj::getRootFromString(string);
    Json::FastWriter fastwriter;
    return fastwriter.write(root);
}

PYBIND11_MODULE(json_fixer, m) {
    m.def("fix_json_file", &fix_json_file, "A function that reads a JSON file in a very lenient way");
    m.def("fix_json_string", &fix_json_string, "A function that reads a JSON string in a very lenient way");
}
