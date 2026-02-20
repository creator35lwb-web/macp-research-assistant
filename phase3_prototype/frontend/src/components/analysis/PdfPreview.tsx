interface PdfPreviewProps {
  arxivId: string;
}

export function PdfPreview({ arxivId }: PdfPreviewProps) {
  // Convert arxiv:XXXX.XXXXX to arXiv PDF URL
  const cleanId = arxivId.replace("arxiv:", "");
  const pdfUrl = `https://arxiv.org/pdf/${cleanId}`;

  return (
    <div className="analysis-section">
      <h4>PDF Preview</h4>
      <iframe
        src={pdfUrl}
        className="pdf-preview"
        title={`PDF: ${cleanId}`}
      />
    </div>
  );
}
