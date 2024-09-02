import { toast } from "@/components/ui/use-toast";
import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function handleCopy(text: string, targetName: string) {
  navigator.clipboard
    .writeText(text)
    .then(() => {
      toast({
        title: "Copied to clipboard",
        description: `The ${targetName} has been copied to your clipboard.`,
        duration: 3000,
      });
    })
    .catch((err) => {
      // eslint-disable-next-line no-console
      console.error("Failed to copy text: ", err);
      toast({
        title: "Copy failed",
        description: `Failed to copy the ${targetName}. Please try again.`,
        variant: "destructive",
        duration: 3000,
      });
    });
}

export function capitaliseFirstLetter(string: string) {
  return string.charAt(0).toUpperCase() + string.slice(1);
}
