import { useState } from "react";

interface NoteEditorProps {
  paperId?: string;
  onSave: (content: string, tags: string[], paperId?: string) => void;
}

export function NoteEditor({ paperId, onSave }: NoteEditorProps) {
  const [content, setContent] = useState("");
  const [tagsInput, setTagsInput] = useState("");

  const handleSave = () => {
    if (!content.trim()) return;
    const tags = tagsInput.split(",").map((t) => t.trim()).filter(Boolean);
    onSave(content, tags, paperId);
    setContent("");
    setTagsInput("");
  };

  return (
    <div className="note-editor">
      <textarea
        placeholder="Write a research note..."
        value={content}
        onChange={(e) => setContent(e.target.value)}
      />
      <div style={{ display: "flex", gap: 8, marginTop: 8 }}>
        <input
          type="text"
          placeholder="Tags (comma-separated)"
          value={tagsInput}
          onChange={(e) => setTagsInput(e.target.value)}
          style={{
            flex: 1, padding: "4px 8px", background: "var(--bg-tertiary)",
            border: "1px solid var(--border-default)", borderRadius: 4,
            color: "var(--text-primary)", fontSize: 13,
          }}
        />
        <button className="btn btn-primary btn-sm" onClick={handleSave} disabled={!content.trim()}>
          Save Note
        </button>
      </div>
    </div>
  );
}
