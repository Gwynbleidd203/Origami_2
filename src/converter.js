import { PDFDocument, rgb } from 'pdf-lib';
import fs from 'fs';

async function resizePDFToA4(inputFilePath, outputFilePath) {
    // Load PDF file
    const pdfBytes = fs.readFileSync(inputFilePath);
    const pdfDoc = await PDFDocument.load(pdfBytes);

    // Resize pages to A4 dimensions
    const pages = pdfDoc.getPages();
    for (const page of pages) {
        const { width, height } = page.getSize();
        const aspectRatio = width / height;

        // A4 dimensions in points
        const a4Width = 595; // 210mm converted to points (1mm = 2.835 points)
        const a4Height = 842; // 297mm converted to points (1mm = 2.835 points)

        let newWidth, newHeight;
        if (aspectRatio > 1) {
            newWidth = a4Width;
            newHeight = a4Width / aspectRatio;
        } else {
            newWidth = a4Height * aspectRatio;
            newHeight = a4Height;
        }

        page.setSize(newWidth, newHeight);
    }

    // Save resized PDF
    const resizedPdfBytes = await pdfDoc.save();
    fs.writeFileSync(outputFilePath, resizedPdfBytes);
}

// Example usage
const inputFilePath = 'input.pdf';
const outputFilePath = 'resized.pdf';
resizePDFToA4(inputFilePath, outputFilePath)
    .then(() => console.log('PDF resized successfully'))
    .catch(error => console.error('Error resizing PDF:', error));
