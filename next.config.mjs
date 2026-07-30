/** @type {import('next').NextConfig} */
const nextConfig = {
  trailingSlash: true,
  async rewrites() {
    return [
      { source: "/", destination: "/index.html" },
      {
        source: "/projects/octoavatar",
        destination: "/projects/octoavatar/index.html"
      }
    ];
  }
};

export default nextConfig;
