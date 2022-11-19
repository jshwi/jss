const path = require("path");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const CssMinimizerPlugin = require("css-minimizer-webpack-plugin");
const TerserPlugin = require("terser-webpack-plugin");
const { DefinePlugin, ProvidePlugin } = require("webpack");
const WorkboxPlugin = require("workbox-webpack-plugin");

const debug = process.env.NODE_ENV !== "production";
const ProductionPlugins = [
  new DefinePlugin({
    "process.env": {
      NODE_ENV: JSON.stringify("production"),
    },
  }),
];
const minimizerPlugins = [new CssMinimizerPlugin(), new TerserPlugin()];

// noinspection JSUnresolvedFunction
module.exports = {
  mode: process.env.NODE_ENV,
  devtool: "inline-source-map",
  entry: {
    index: "./assets/js/index.js",
    main_css: [
      "@fortawesome/fontawesome-free/css/all.css",
      "bootstrap/dist/css/bootstrap.css",
      "bootstrap4-toggle/css/bootstrap4-toggle.min.css",
      "bootstrap-icons/font/bootstrap-icons.css",
      "./assets/css/style.css",
      "./assets/css/highlight/default.css",
    ],
  },
  output: {
    path: path.join(__dirname, "app", "static"),
    filename: "[name].bundle.js",
    chunkFilename: "[id].js",
    publicPath: "/static/",
    library: "[name]",
    clean: true,
  },
  resolve: { extensions: [".js", ".css"] },
  plugins: [
    new MiniCssExtractPlugin({ filename: "[name].bundle.css" }),
    new ProvidePlugin({ $: "jquery", jQuery: "jquery" }),
    new WorkboxPlugin.GenerateSW({
      clientsClaim: true,
      skipWaiting: true,
      maximumFileSizeToCacheInBytes: 3000000,
    }),
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
