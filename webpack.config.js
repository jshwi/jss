const path = require("path");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const CssMinimizerPlugin = require("css-minimizer-webpack-plugin");
const TerserPlugin = require("terser-webpack-plugin");
const { DefinePlugin, ProvidePlugin } = require("webpack");
const WebpackPwaManifest = require("webpack-pwa-manifest");
const WorkboxPlugin = require("workbox-webpack-plugin");

const CWD = path.resolve(__dirname);
const ASSETS = path.join(CWD, "assets");
const ASSETS_JS = path.join(ASSETS, "js");
const ASSETS_CSS = path.join(ASSETS, "css");
const ASSETS_IMG = path.join(ASSETS, "img");

const debug = process.env.NODE_ENV !== "production";
const ProductionPlugins = [
  new DefinePlugin({
    "process.env": {
      NODE_ENV: JSON.stringify("production"),
    },
  }),
];
const minimizerPlugins = [new CssMinimizerPlugin(), new TerserPlugin()];
const siteWebmanifest = {
  filename: "site.webmanifest",
  name: "Jshwi Solutions",
  short_name: "JSS",
  description: "A Flask web app",
  theme_color: "#ffffff",
  background_color: "#ffffff",
  start_url: "/",
  display: "standalone",
  scope: "/",
  icons: [
    {
      src: path.join(ASSETS_IMG, "favicon.ico"),
      size: "48x48",
    },
    {
      src: path.join(ASSETS_IMG, "android-chrome-192x192.png"),
      size: "192x192",
      purpose: "maskable",
    },
    {
      src: path.join(ASSETS_IMG, "android-chrome-512x512.png"),
      size: "512x512",
      purpose: "maskable",
    },
    {
      src: path.join(ASSETS_IMG, "apple-touch-icon.png"),
      size: "180x180",
      purpose: "maskable",
    },
    {
      src: path.join(ASSETS_IMG, "favicon-16x16.png"),
      size: "16x16",
    },
    {
      src: path.join(ASSETS_IMG, "favicon-32x32.png"),
      size: "32x32",
    },
    {
      src: path.join(ASSETS_IMG, "mstile-150x150.png"),
      size: "270x270",
    },
    {
      src: path.join(ASSETS_IMG, "safari-pinned-tab.svg"),
      size: "683x683",
    },
  ],
  fingerprints: false,
};

// noinspection JSUnresolvedFunction
module.exports = {
  mode: process.env.NODE_ENV,
  devtool: "inline-source-map",
  entry: {
    main_js: path.join(ASSETS_JS, "index"),
    main_css: [
      path.join("@fortawesome", "fontawesome-free", "css", "all.css"),
      path.join("bootstrap", "dist", "css", "bootstrap.css"),
      path.join("bootstrap4-toggle", "css", "bootstrap4-toggle.min.css"),
      path.join("bootstrap-icons", "font", "bootstrap-icons.css"),
      path.join(ASSETS_CSS, "style.css"),
      path.join(ASSETS_CSS, "highlight", "default.css"),
    ],
  },
  output: {
    path: path.join(__dirname, "app", "static", "build"),
    filename: "[name].bundle.js",
    chunkFilename: "[id].js",
    publicPath: "/static/build/",
    library: "[name]",
    clean: true,
  },
  resolve: { extensions: [".js", ".css"] },
  plugins: [
    new MiniCssExtractPlugin({ filename: "[name].bundle.css" }),
    new ProvidePlugin({ $: "jquery", jQuery: "jquery" }),
    new WebpackPwaManifest(siteWebmanifest),
    new WorkboxPlugin.GenerateSW({ clientsClaim: true, skipWaiting: true }),
  ].concat(debug ? [] : ProductionPlugins),
  module: {
    rules: [
      {
        test: /\.css$/,
        use: [{ loader: MiniCssExtractPlugin.loader }, "css-loader"],
      },
      {
        test: /\.woff(2)?(\?v=\d\.\d\.\d)?$/,
        loader: "url-loader",
        options: { limit: 10000, mimetype: "application/font-woff" },
      },
      {
        test: /\.(ttf|eot|svg|png|jpe?g|gif|ico|xml)(\?.*)?$/i,
        loader: "file-loader",
        options: { name: "[name].[ext]" },
      },
      {
        test: /\.js$/,
        exclude: /node_modules/,
        loader: "babel-loader",
        options: { presets: ["@babel/preset-env"], cacheDirectory: true },
      },
    ],
  },
  optimization: {
    minimize: debug !== true,
    minimizer: [].concat(debug ? [] : minimizerPlugins),
  },
};
