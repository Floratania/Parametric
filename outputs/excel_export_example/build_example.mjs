import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const outDir = "C:/Users/tania/Parametric/outputs/excel_export_example";
await fs.mkdir(outDir, { recursive: true });

const workbook = Workbook.create();
const exportSheet = workbook.worksheets.add("Експорт");
const helpSheet = workbook.worksheets.add("Довідка");

exportSheet.showGridLines = false;
exportSheet.getRange("A1:I1").values = [[
  "model", "target_width", "target_height", "target_opening",
  "text", "font_size", "font", "keep_blocks", "delete_blocks",
]];
exportSheet.getRange("A2:I4").values = [
  ["Door_A", 900, 2100, "right", "45", 30, "STANDARD", "Полотно,Рама,Поріг", "Підсилювач"],
  ["Door_B", 1000, 2200, "left", "60", 30, "STANDARD", "Полотно,Рама,Поріг", "Підсилювач"],
  ["Door_A", 860, 2040, "left", "45", 25, "STANDARD", "Полотно,Рама", "Поріг"],
];
exportSheet.getRange("A1:I1").format = {
  fill: "#1F4E78",
  font: { bold: true, color: "#FFFFFF" },
  horizontalAlignment: "center",
  verticalAlignment: "center",
  wrapText: true,
  borders: { preset: "outside", style: "medium", color: "#1F4E78" },
};
exportSheet.getRange("A2:I4").format = {
  fill: "#F7FAFC",
  font: { color: "#1F2937" },
  verticalAlignment: "center",
  borders: { preset: "inside", style: "thin", color: "#D9E2F3" },
};
exportSheet.getRange("B2:C4").format.numberFormat = "0";
exportSheet.getRange("F2:F4").format.numberFormat = "0";
exportSheet.getRange("B2:C4").format.horizontalAlignment = "right";
exportSheet.getRange("D2:G4").format.horizontalAlignment = "center";
exportSheet.getRange("A1:A4").format.columnWidth = 18;
exportSheet.getRange("B1:C4").format.columnWidth = 16;
exportSheet.getRange("D1:D4").format.columnWidth = 19;
exportSheet.getRange("E1:E4").format.columnWidth = 12;
exportSheet.getRange("F1:F4").format.columnWidth = 12;
exportSheet.getRange("G1:G4").format.columnWidth = 14;
exportSheet.getRange("H1:I4").format.columnWidth = 25;
exportSheet.getRange("1:1").format.rowHeight = 34;
exportSheet.getRange("2:4").format.rowHeight = 24;
exportSheet.freezePanes.freezeRows(1);
exportSheet.getRange("D2:D100").dataValidation = {
  rule: { type: "list", values: ["left", "right"] },
};
const exportTable = exportSheet.tables.add("A1:I4", true, "ExportJobs");
exportTable.style = "TableStyleMedium2";
exportTable.showBandedRows = true;
exportTable.showFilterButton = true;

helpSheet.showGridLines = false;
helpSheet.getRange("A1:D1").merge();
helpSheet.getRange("A1").values = [["Приклад Excel для пакетного експорту DXF"]];
helpSheet.getRange("A1:D1").format = {
  fill: "#1F4E78",
  font: { bold: true, color: "#FFFFFF", size: 16 },
  horizontalAlignment: "center",
  verticalAlignment: "center",
};
helpSheet.getRange("A3:D3").values = [["Колонка", "Обов'язкова", "Приклад", "Призначення"]];
helpSheet.getRange("A4:D12").values = [
  ["model", "так*", "Door_A", "Назва моделі у БД. Замість неї можна використати model_id."],
  ["target_width", "так", 900, "Нова ширина дверей W у мм."],
  ["target_height", "так", 2100, "Нова висота дверей H у мм."],
  ["target_opening", "ні", "right", "Нове відкривання: left або right."],
  ["text", "ні", "45", "Текст для попередньо заданого текстового блока."],
  ["font_size", "ні", 30, "Висота тексту."],
  ["font", "ні", "STANDARD", "DXF-стиль шрифту."],
  ["keep_blocks", "ні", "Полотно,Рама", "Групи, які треба залишити; розділяються комою."],
  ["delete_blocks", "ні", "Підсилювач", "Групи, які треба видалити; розділяються комою."],
];
helpSheet.getRange("A14:D14").merge();
helpSheet.getRange("A14").values = [[
  "* Для точного вибору моделі використовуйте model_id замість model. Один рядок = один розмір однієї моделі.",
]];
helpSheet.getRange("A3:D3").format = {
  fill: "#D9EAF7",
  font: { bold: true, color: "#17365D" },
  horizontalAlignment: "center",
  borders: { preset: "outside", style: "medium", color: "#9FBAD0" },
};
helpSheet.getRange("A4:D12").format = {
  fill: "#FFFFFF",
  verticalAlignment: "top",
  wrapText: true,
  borders: { preset: "inside", style: "thin", color: "#D9E2F3" },
};
helpSheet.getRange("A14:D14").format = {
  fill: "#FFF2CC",
  font: { italic: true, color: "#7F6000" },
  wrapText: true,
  verticalAlignment: "center",
};
helpSheet.getRange("A1:A14").format.columnWidth = 20;
helpSheet.getRange("B1:B14").format.columnWidth = 14;
helpSheet.getRange("C1:C14").format.columnWidth = 22;
helpSheet.getRange("D1:D14").format.columnWidth = 58;
helpSheet.getRange("1:1").format.rowHeight = 34;
helpSheet.getRange("3:3").format.rowHeight = 28;
helpSheet.getRange("4:12").format.rowHeight = 34;
helpSheet.getRange("14:14").format.rowHeight = 42;
helpSheet.freezePanes.freezeRows(3);

const output = await SpreadsheetFile.exportXlsx(workbook);
const xlsxPath = path.join(outDir, "parametric_export_example.xlsx");
await output.save(xlsxPath);

const preview = await workbook.render({
  sheetName: "Експорт",
  range: "A1:I4",
  scale: 1.5,
  format: "png",
});
await fs.writeFile(
  path.join(outDir, "parametric_export_example_preview.png"),
  new Uint8Array(await preview.arrayBuffer()),
);

const inspection = await workbook.inspect({
  kind: "table",
  range: "Експорт!A1:I4",
  include: "values,formulas",
  tableMaxRows: 10,
  tableMaxCols: 12,
});
const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 100 },
  summary: "final formula error scan",
});
console.log(JSON.stringify({ xlsxPath, inspection: inspection.ndjson, errors: errors.ndjson }));
