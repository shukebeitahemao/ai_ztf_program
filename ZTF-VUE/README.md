# AI-ZTF

This template should help get you started developing with Vue 3 in Vite.

## Recommended IDE Setup
# ZTF-VUE 项目

一个基于 Vue 3 的前端项目。

## 🚀 快速开始

### 前置要求
确保已安装以下环境：
- [Node.js](https://nodejs.org/) (推荐 LTS 版本)
- npm (通常随 Node.js 一起安装)

### 安装与运行
1. ​**克隆项目**​
   ```bash
   git clone https://github.com/your-username/ZTF-VUW.git
2.**进入目录**
cd ZTF-VUE
3.**安装依赖**
npm install
4.**启动开发服务器**
npm run dev
5.**​打开浏览器​**
开发服务器通常会在 http://localhost:3000 启动（具体端口请查看终端输出）


[VSCode](https://code.visualstudio.com/) + [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (and disable Vetur).

## Type Support for `.vue` Imports in TS

TypeScript cannot handle type information for `.vue` imports by default, so we replace the `tsc` CLI with `vue-tsc` for type checking. In editors, we need [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) to make the TypeScript language service aware of `.vue` types.

## Customize configuration

See [Vite Configuration Reference](https://vite.dev/config/).

## Project Setup

```sh
npm install
```

### Compile and Hot-Reload for Development

```sh
npm run dev
```

### Type-Check, Compile and Minify for Production

```sh
npm run build
```

### Run Unit Tests with [Vitest](https://vitest.dev/)

```sh
npm run test:unit
```

### Run End-to-End Tests with [Playwright](https://playwright.dev)

```sh
# Install browsers for the first run
npx playwright install

# When testing on CI, must build the project first
npm run build

# Runs the end-to-end tests
npm run test:e2e
# Runs the tests only on Chromium
npm run test:e2e -- --project=chromium
# Runs the tests of a specific file
npm run test:e2e -- tests/example.spec.ts
# Runs the tests in debug mode
npm run test:e2e -- --debug
```

### Lint with [ESLint](https://eslint.org/)

```sh
npm run lint
```
