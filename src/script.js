import { PDFDocument, PDFPage } from 'pdf-lib';
import fs from 'fs';


async function convertToA4(inputPath, outputPath) {
    // Read input PDF file
    const inputPdfBytes = fs.readFileSync(inputPath);

    // Create a new PDF document
    const pdfDoc = await PDFDocument.create();
    const [width, height] = PDFPage.getPageSize('A4');

    // Add pages from input PDF to the new document
    const inputPdfDoc = await PDFDocument.load(inputPdfBytes);
    for (const inputPage of inputPdfDoc.getPages()) {
        const [inputWidth, inputHeight] = inputPage.getSize();
        const page = pdfDoc.addPage([width, height]);
        const scaleFactor = Math.min(width / inputWidth, height / inputHeight);
        const { x, y } = page.getSize();
        const offsetX = (x - inputWidth * scaleFactor) / 2;
        const offsetY = (y - inputHeight * scaleFactor) / 2;
        page.drawImage(inputPage, {
            x: offsetX,
            y: offsetY,
            width: inputWidth * scaleFactor,
            height: inputHeight * scaleFactor,
        });
    }

    // Save the new PDF document
    const modifiedPdfBytes = await pdfDoc.save();
    fs.writeFileSync(outputPath, modifiedPdfBytes);
}

// Example usage
const inputFilePath = 'dummy.pdf';
const outputFilePath = 'output.pdf';
convertToA4(inputFilePath, outputFilePath)
    .then(() => console.log('Conversion complete!'))
    .catch(error => console.error('Conversion error:', error));
