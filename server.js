const http = require("http");
const fs = require("fs");
const path = require("path");

const port = 8080;

const server = http.createServer((req, res) => {
  console.log("Request:", req.method, req.url);

  // Proxy API requests to backend
  if (req.url.startsWith("/api/")) {
    console.log("Proxying API request to backend:", req.url);

    const options = {
      hostname: "backend",
      port: 8000,
      path: req.url,
      method: req.method,
      headers: req.headers
    };

    const proxyReq = http.request(options, (proxyRes) => {
      console.log("Backend response:", proxyRes.statusCode);
      res.writeHead(proxyRes.statusCode, proxyRes.headers);
      proxyRes.pipe(res);
    });

    proxyReq.on("error", (err) => {
      console.error("Proxy error:", err);
      res.writeHead(500);
      res.end("Proxy error");
    });

    req.pipe(proxyReq);
    return;
  }

  // Serve static files
  let filePath = path.join(__dirname, "dist", req.url === "/" ? "index.html" : req.url);

  console.log("Serving static file:", req.url, "->", filePath);

  if (!fs.existsSync(filePath) || fs.statSync(filePath).isDirectory()) {
    filePath = path.join(__dirname, "dist", "index.html");
    console.log("Serving index.html instead:", filePath);
  }

  const ext = path.extname(filePath);
  const contentType = {
    ".html": "text/html",
    ".css": "text/css",
    ".js": "application/javascript",
    ".json": "application/json",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".gif": "image/gif",
    ".svg": "image/svg+xml",
  }[ext] || "text/plain";

  fs.readFile(filePath, (err, data) => {
    if (err) {
      console.error("File not found:", filePath, err.message);
      res.writeHead(404);
      res.end("File not found");
      return;
    }
    console.log("Serving file:", filePath, "as", contentType);
    res.writeHead(200, { "Content-Type": contentType });
    res.end(data);
  });
});

server.listen(port, () => {
  console.log(`Frontend server running at http://localhost:${port}`);
  console.log(`API requests will be proxied to backend service`);
  console.log("Serving files from:", path.join(__dirname, "dist"));
});
