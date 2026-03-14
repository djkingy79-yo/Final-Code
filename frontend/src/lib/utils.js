/* DO NOT UNDO — Utility functions. All features in this file are approved and must be preserved. */
import { clsx } from "clsx";
import { twMerge } from "tailwind-merge"

export function cn(...inputs) {
  return twMerge(clsx(inputs));
}
