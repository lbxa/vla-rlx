import { defineCollection } from "astro:content";
import { glob } from "astro/loaders";
import { z } from "astro/zod";

const sections = defineCollection({
  loader: glob({ base: "./src/content/sections", pattern: "**/*.mdx" }),
  schema: z
    .object({
      order: z.number(),
      title: z.string().optional(),
      slug: z.string().optional(),
    })
    .superRefine((data, ctx) => {
      const anchor = data.slug?.trim() || data.title?.trim();
      if (!anchor) {
        ctx.addIssue({
          code: "custom",
          message: "Provide title and/or slug.",
          path: ["title"],
        });
      }
    }),
});

export const collections = {
  sections,
};
