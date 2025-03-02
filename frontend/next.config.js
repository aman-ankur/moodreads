/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'covers.openlibrary.org',
        pathname: '/b/isbn/**',
      },
      {
        protocol: 'https',
        hostname: 'covers.openlibrary.org',
        pathname: '/b/olid/**',
      },
      {
        protocol: 'https',
        hostname: 'books.google.com',
        pathname: '/books/content**',
      },
      {
        protocol: 'https',
        hostname: 'books.google.com',
        pathname: '/books/**',
      },
      {
        protocol: 'https',
        hostname: 'via.placeholder.com',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'images.unsplash.com',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'images-na.ssl-images-amazon.com',
        pathname: '/**',
      },
    ],
  },
  output: 'standalone',
};

module.exports = nextConfig; 