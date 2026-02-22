import { useEffect, useState } from "react";

export interface ToastMessage {
  id: number;
  type: "success" | "error" | "info";
  text: string;
}

let toastId = 0;
let addToastFn: ((msg: Omit<ToastMessage, "id">) => void) | null = null;

/** Global toast trigger — call from anywhere */
export function showToast(type: ToastMessage["type"], text: string) {
  if (addToastFn) addToastFn({ type, text });
}

export function ToastContainer() {
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  useEffect(() => {
    addToastFn = (msg) => {
      const id = ++toastId;
      setToasts((prev) => [...prev, { ...msg, id }]);
      setTimeout(() => setToasts((prev) => prev.filter((t) => t.id !== id)), 4000);
    };
    return () => { addToastFn = null; };
  }, []);

  if (toasts.length === 0) return null;

  return (
    <div style={{
      position: "fixed", bottom: 20, right: 20, zIndex: 9999,
      display: "flex", flexDirection: "column", gap: 8,
    }}>
      {toasts.map((t) => (
        <div
          key={t.id}
          style={{
            padding: "10px 16px",
            borderRadius: 8,
            color: "#fff",
            fontSize: 14,
            fontWeight: 500,
            boxShadow: "0 4px 12px rgba(0,0,0,0.3)",
            animation: "toast-in 0.3s ease",
            background: t.type === "success" ? "#22c55e"
              : t.type === "error" ? "#ef4444"
              : "#3b82f6",
          }}
        >
          {t.type === "success" ? "\u2713 " : t.type === "error" ? "\u2717 " : "\u2139 "}
          {t.text}
        </div>
      ))}
    </div>
  );
}
