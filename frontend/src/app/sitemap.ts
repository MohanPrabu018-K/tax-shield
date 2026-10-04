import type { MetadataRoute } from 'next';

export default function sitemap(): MetadataRoute.Sitemap {
  const base = process.env.NEXT_PUBLIC_SITE_URL ?? 'http://localhost:3000';
  const now = new Date();
  return [
    { url: `${base}/`, lastModified: now },
    { url: `${base}/login`, lastModified: now },
    { url: `${base}/register`, lastModified: now },
    { url: `${base}/pricing`, lastModified: now },
    { url: `${base}/security`, lastModified: now },
    { url: `${base}/privacy`, lastModified: now },
    { url: `${base}/terms`, lastModified: now },
    { url: `${base}/refund-policy`, lastModified: now },
    { url: `${base}/acceptable-use`, lastModified: now },
    { url: `${base}/disclaimer`, lastModified: now },
    { url: `${base}/cookie-policy`, lastModified: now },
    { url: `${base}/help`, lastModified: now },
  ];
}
