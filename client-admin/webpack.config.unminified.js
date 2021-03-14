// Copyright (C) 2012-present, The Authors. This program is free software: you can redistribute it and/or  modify it under the terms of the GNU Affero General Public License, version 3, as published by the Free Software Foundation. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.

let POLIS_ROOT = process.env.POLIS_ROOT
var config = require(POLIS_ROOT + 'config/config.js');

var path = require("path");
var webpack = require("webpack");
var CompressionPlugin = require('compression-webpack-plugin')

module.exports = {
  entry: ["./src/index"],
  output: {
    path: path.join(__dirname, "dist"),
    filename: "admin_bundle.js",
    publicPath: "/dist/",
  },
  resolve: {
    extensions: [".js", ".css", ".png", ".svg"],
  },
  plugins: [
    new CompressionPlugin({
      test: /\.js$/,
      // Leave unmodified without gz ext.
      // See: https://webpack.js.org/plugins/compression-webpack-plugin/#options
      filename: '[path][base]',
      deleteOriginalAssets: true,
    }),
    new webpack.DefinePlugin({
      config.get('env'): JSON.stringify("development"),
    }),
  ],
  optimization: {
    minimize: false, //Update this to true or false
  },
  module: {
    rules: [
      {
        test: /\.m?js$/,
        exclude: /(node_modules|bower_components)/,
        use: {
          loader: "babel-loader",
          options: {
            presets: ["@babel/preset-env"],
          },
        },
      },
      {
        test: /\.(png|jpg|gif|svg)$/,
        loader: "file-loader",
      },
    ],
  },
};
