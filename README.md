# OpenHexagonLevelConverter
A tool to automatically port Open Hexagon 1.92 Levels to the new Open Hexagon
# Issues
- This tool does not support all events it could
- Certain things that were possible in 1.92 cannot be done in the new version
- timings may feel very slightly different due to 1.92 using `sf::clock` which causes significant timing fluctuations compared to `std::chrono` which is used in the new version
- styles seem to look different
- pulse and beatpulse initial delay are off
# Usage
`python main.py <path/to/1.92/pack/folder> <path/to/where/the/port/will/be/created>`
