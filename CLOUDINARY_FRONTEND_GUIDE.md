# ☁️ Cloudinary Frontend Integration Guide

This application has officially migrated to **Cloudinary** for scalable, secure, and fast image delivery. All new user uploads (like Event Images) are now processed externally and returned as full HTTPS CDN URLs, rather than local filesystem paths.

---

## 🏗️ 1. What Changes for the API Responses?

Previously, when fetching an Event or Profile, the `picture` property returned a relative string:
```json
{
  "id": 2,
  "event_name": "Premium Night",
  "picture": "uploads/1774216181.812595-virtual2d.jpg"
}
```

**Now, the backend will return an absolute Cloudinary URL:**
```json
{
  "id": 2,
  "event_name": "Premium Night",
  "picture": "https://res.cloudinary.com/your-cloud-name/image/upload/v123456789/filename.jpg"
}
```

---

## 💻 2. Handling Backward Compatibility in UI

Since the database still contains **older records** that use the local `uploads/...` format, your frontend code MUST elegantly handle both relative strings *and* full HTTP strings.

### ✅ Recommended Pattern (React / Vue)
Create a utility function to format the image source safely:

```javascript
export const getProcessedImageUrl = (picturePath) => {
  if (!picturePath) return "/placeholder-image.png"; // Fallback image
  
  // If it's already a Cloudinary URL (or any absolute URL), return it directly.
  if (picturePath.startsWith("http://") || picturePath.startsWith("https://")) {
    return picturePath;
  }
  
  // If it's a legacy relative path, append the backend base URL.
  return `${process.env.NEXT_PUBLIC_API_URL}/${picturePath}`;
};
```

**Usage in Component:**
```jsx
<img 
  src={getProcessedImageUrl(event.picture)} 
  alt={event.event_name} 
  className="w-full h-auto object-cover rounded-md"
/>
```

---

## ⚡ 3. Next.js Configurations (IMPORTANT)

If you are using Next.js and the `next/image` component, you will get an **Invalid src prop** error unless you whitelist `res.cloudinary.com`.

Update your `next.config.js` or `next.config.mjs`:

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'res.cloudinary.com',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'app.samdavweb.org.ng', // Legacy domain support
        pathname: '/uploads/**',
      }
    ]
  }
}

module.exports = nextConfig;
```

---

## 🖼️ 4. Advanced: Using Cloudinary Transformations (Optional)

Because we are returning raw Cloudinary URLs, the frontend can manipulate the image dynamically (e.g., resizing, cropping, compressing) simply by injecting parameters into the URL.

If your URL looks like this:
`https://res.cloudinary.com/demo/image/upload/sample.jpg`

You can transform it on the fly by adding `w_500,h_500,c_fill,q_auto,f_auto`:
`https://res.cloudinary.com/demo/image/upload/w_500,h_500,c_fill,q_auto,f_auto/sample.jpg`

*This dramatically improves frontend load times for mobile users!*

---

## 🚀 5. File Uploads (FormData)
You do **not** need to change how you send data to the backend API.
Continue sending the raw file over `multipart/form-data` during event creation. The backend automatically intercepts the file bytes, streams them directly to Cloudinary, and saves the resulting CDN URL to the database.
