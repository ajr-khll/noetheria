"use client";

import { FiAlertTriangle } from "react-icons/fi";

interface ConfirmDialogProps {
  isOpen: boolean;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  onConfirm: () => void;
  onCancel: () => void;
  variant?: 'danger' | 'warning' | 'info';
}

export default function ConfirmDialog({
  isOpen,
  title,
  message,
  confirmText = "Confirm",
  cancelText = "Cancel",
  onConfirm,
  onCancel,
  variant = 'danger'
}: ConfirmDialogProps) {
  if (!isOpen) return null;

  const variantStyles = {
    danger: {
      icon: "text-red-400",
      confirmButton: "bg-red-600 hover:bg-red-700 focus:ring-red-500"
    },
    warning: {
      icon: "text-yellow-400",
      confirmButton: "bg-yellow-600 hover:bg-yellow-700 focus:ring-yellow-500"
    },
    info: {
      icon: "text-blue-400",
      confirmButton: "bg-blue-600 hover:bg-blue-700 focus:ring-blue-500"
    }
  };

  const styles = variantStyles[variant];

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-zinc-800 rounded-lg max-w-md w-full border border-zinc-700 shadow-xl">
        <div className="p-6">
          <div className="flex items-center gap-3 mb-4">
            <FiAlertTriangle className={`w-6 h-6 ${styles.icon}`} />
            <h3 className="text-lg font-semibold text-white">{title}</h3>
          </div>
          
          <p className="text-zinc-300 mb-6 leading-relaxed">
            {message}
          </p>
          
          <div className="flex gap-3 justify-end">
            <button
              onClick={onCancel}
              className="px-4 py-2 text-zinc-300 bg-zinc-700 hover:bg-zinc-600 rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-zinc-500"
            >
              {cancelText}
            </button>
            <button
              onClick={onConfirm}
              className={`px-4 py-2 text-white rounded-md transition-colors focus:outline-none focus:ring-2 ${styles.confirmButton}`}
            >
              {confirmText}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}