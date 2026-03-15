const { getDefaultConfig } = require("expo/metro-config");
const path = require("path");

const config = getDefaultConfig(__dirname);

// Force CJS resolution for packages that ship ESM with import.meta (e.g. zustand).
// Metro web bundles are not ES modules, so import.meta breaks at runtime.
config.resolver.unstable_enablePackageExports = false;

module.exports = config;
