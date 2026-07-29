"use client";

import { useState } from "react";
import type { FormEvent } from "react";

import { Button } from "@/components/ui/button";

export default function InputBar({
  onSend,
  disabled,
}: {
  onSend: (message: string) => void;
  disabled?: boolean;
}) {
  const [value, setValue] = useState("");

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const trimmed = value.trim();
    if (!trimmed || disabled) return;

    onSend(trimmed);
    setValue("");
  }

  return (
    <form onSubmit={handleSubmit} className="flex items-end gap-2 border-t border-zinc-800 pt-4">
      <textarea
        value={value}
        onChange={(event) => setValue(event.target.value)}
        onKeyDown={(event) => {
          if (event.key === "Enter" && !event.shiftKey) {
            handleSubmit(event);
          }
        }}
        placeholder="Écris un message à Jarvis..."
        rows={1}
        className="flex-1 resize-none rounded-xl border border-zinc-700 bg-zinc-900/70 px-4 py-2.5 text-sm text-zinc-100 outline-none placeholder:text-zinc-500 focus:border-cyan-400/60"
      />
      <Button type="submit" disabled={disabled || !value.trim()}>
        Envoyer
      </Button>
    </form>
  );
}
