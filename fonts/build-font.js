const fs = require('fs');
const path = require('path');

// 配置要转换的字体（文件名 -> 输出的JS变量名）
const fonts = [
  { input: 'arial.ttf', output: 'arial.js' },
  { input: 'arialbd.ttf', output: 'arialbd.js' }
];

fonts.forEach(font => {
  const inputPath = path.join(__dirname, font.input);
  
  if (!fs.existsSync(inputPath)) {
    console.error(`找不到文件: ${font.input}，请检查是否在 fonts 目录下`);
    return;
  }

  const fontBuffer = fs.readFileSync(inputPath);
  const base64Str = fontBuffer.toString('base64');
  
  // 生成 JS 模块内容
  const jsContent = `module.exports = 'data:font/truetype;charset=utf-8;base64,${base64Str}';`;
  
  const outputPath = path.join(__dirname, font.output);
  fs.writeFileSync(outputPath, jsContent, 'utf8');
  
  console.log(`✅ 成功生成: ${font.output} (原大小: ${(fontBuffer.length / 1024).toFixed(1)} KB)`);
});

console.log('字体打包完成！');