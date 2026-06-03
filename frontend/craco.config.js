// craco.config.js
const path = require("path");
require("dotenv").config();

// ── Production environment validation ──
const deployTarget = (process.env.DEPLOY_TARGET || "").trim().toLowerCase();
const useSameOrigin = (process.env.REACT_APP_USE_SAME_ORIGIN || "").trim().toLowerCase();
const requiresBackendUrl =
  useSameOrigin === "false" || deployTarget === "mobile" || deployTarget === "split";

if (process.env.NODE_ENV === "production" && !process.env.REACT_APP_BACKEND_URL) {
  if (requiresBackendUrl) {
    throw new Error(
      "REACT_APP_BACKEND_URL is required for production builds when " +
        "REACT_APP_USE_SAME_ORIGIN=false or DEPLOY_TARGET=mobile|split."
    );
  }

  // Web deployments (Render/Railway/Docker same-origin) use window.location.origin at runtime
  // and do not require a baked-in backend URL. Mobile builds (Capacitor) DO require it.
  // Keep builds unblocked for same-origin web deploys unless the build flags say otherwise.
  // Mobile builds are additionally guarded in frontend/build-mobile.sh.
  // eslint-disable-next-line no-console
  console.warn(
    "REACT_APP_BACKEND_URL is not set. Defaulting to same-origin runtime API calls. " +
      "Set REACT_APP_USE_SAME_ORIGIN=false (or DEPLOY_TARGET=mobile|split) to require it at build time."
  );
}

// Check if we're in development/preview mode (not production build)
// Craco sets NODE_ENV=development for start, NODE_ENV=production for build
const isDevServer = process.env.NODE_ENV !== "production";

// Environment variable overrides
const config = {
  enableHealthCheck: process.env.ENABLE_HEALTH_CHECK === "true",
  enableVisualEdits: false, // Disabled to prevent build crashes from metadata plugin
};

// Conditionally load visual edits modules only in dev mode
let setupDevServer;
let babelMetadataPlugin;

if (config.enableVisualEdits) {
  setupDevServer = require("./plugins/visual-edits/dev-server-setup");
  babelMetadataPlugin = require("./plugins/visual-edits/babel-metadata-plugin");
}

// Conditionally load health check modules only if enabled
let WebpackHealthPlugin;
let setupHealthEndpoints;
let healthPluginInstance;

if (config.enableHealthCheck) {
  WebpackHealthPlugin = require("./plugins/health-check/webpack-health-plugin");
  setupHealthEndpoints = require("./plugins/health-check/health-endpoints");
  healthPluginInstance = new WebpackHealthPlugin();
}

const webpackConfig = {
  eslint: {
    configure: {
      extends: ["plugin:react-hooks/recommended"],
      rules: {
        "react-hooks/rules-of-hooks": "error",
        "react-hooks/exhaustive-deps": "warn",
      },
    },
  },
  webpack: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
    configure: (webpackConfig) => {

      // ── Code Splitting — break the 7MB bundle into smaller chunks ──
      // Custom domain proxy (Cloudflare) returns 520 on large files.
      // Split into vendor chunks < 500KB each.
      if (!isDevServer) {
        webpackConfig.optimization = {
          ...webpackConfig.optimization,
          splitChunks: {
            chunks: 'all',
            maxSize: 400000, // 400KB max per chunk
            cacheGroups: {
              radix: {
                test: /[\\/]node_modules[\\/]@radix-ui[\\/]/,
                name: 'vendor-radix',
                priority: 30,
                reuseExistingChunk: true,
              },
              capacitor: {
                test: /[\\/]node_modules[\\/]@capacitor[\\/]/,
                name: 'vendor-capacitor',
                priority: 25,
                reuseExistingChunk: true,
              },
              react: {
                test: /[\\/]node_modules[\\/](react|react-dom|react-router|scheduler)[\\/]/,
                name: 'vendor-react',
                priority: 20,
                reuseExistingChunk: true,
              },
              vendor: {
                test: /[\\/]node_modules[\\/]/,
                name: 'vendor-misc',
                priority: 10,
                reuseExistingChunk: true,
              },
            },
          },
        };
      }

      // Add ignored patterns to reduce watched directories
        webpackConfig.watchOptions = {
          ...webpackConfig.watchOptions,
          ignored: [
            '**/node_modules/**',
            '**/.git/**',
            '**/build/**',
            '**/dist/**',
            '**/coverage/**',
            '**/public/**',
        ],
      };

      // Add health check plugin to webpack if enabled
      if (config.enableHealthCheck && healthPluginInstance) {
        webpackConfig.plugins.push(healthPluginInstance);
      }
      return webpackConfig;
    },
  },
};

// Only add babel metadata plugin during dev server
if (config.enableVisualEdits && babelMetadataPlugin) {
  webpackConfig.babel = {
    plugins: [babelMetadataPlugin],
  };
}

webpackConfig.devServer = (devServerConfig) => {
  // Enable compression to reduce bundle transfer size
  // Custom domain Cloudflare proxy fails on large uncompressed responses
  devServerConfig.compress = true;

  // Apply visual edits dev server setup only if enabled
  if (config.enableVisualEdits && setupDevServer) {
    devServerConfig = setupDevServer(devServerConfig);
  }

  // Add health check endpoints if enabled
  if (config.enableHealthCheck && setupHealthEndpoints && healthPluginInstance) {
    const originalSetupMiddlewares = devServerConfig.setupMiddlewares;

    devServerConfig.setupMiddlewares = (middlewares, devServer) => {
      // Call original setup if exists
      if (originalSetupMiddlewares) {
        middlewares = originalSetupMiddlewares(middlewares, devServer);
      }

      // Setup health endpoints
      setupHealthEndpoints(devServer, healthPluginInstance);

      return middlewares;
    };
  }

  return devServerConfig;
};

module.exports = webpackConfig;
