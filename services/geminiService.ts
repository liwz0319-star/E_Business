
import { GoogleGenAI, Type } from "@google/genai";

export enum GenerationType {
  TEXT = 'Text Content',
  IMAGE = 'Product Image',
  VIDEO = 'Ad Video',
  SEARCH = 'Market Insight'
}

const ai = new GoogleGenAI({ apiKey: process.env.API_KEY || '' });

export const generateContent = async (prompt: string, type: GenerationType): Promise<any> => {
  // Simple check for API key
  if (!process.env.API_KEY) {
      // Return mock data for demo if no API key is present
      return mockData(type);
  }

  try {
    switch (type) {
      case GenerationType.IMAGE:
        const imgResponse = await ai.models.generateContent({
          model: 'gemini-2.5-flash-image',
          contents: { parts: [{ text: prompt }] },
          config: { imageConfig: { aspectRatio: "16:9" } }
        });
        const imagePart = imgResponse.candidates?.[0]?.content?.parts.find(p => p.inlineData);
        return imagePart ? `data:image/png;base64,${imagePart.inlineData.data}` : mockData(type);

      case GenerationType.VIDEO:
        // Veo model requires selected key usually, but following standard flow
        let op = await ai.models.generateVideos({
          model: 'veo-3.1-fast-generate-preview',
          prompt: prompt,
          config: { resolution: '720p', aspectRatio: '16:9' }
        });
        while (!op.done) {
          await new Promise(r => setTimeout(r, 5000));
          op = await ai.operations.getVideosOperation({ operation: op });
        }
        const downloadLink = op.response?.generatedVideos?.[0]?.video?.uri;
        const vidResponse = await fetch(`${downloadLink}&key=${process.env.API_KEY}`);
        const blob = await vidResponse.blob();
        return URL.createObjectURL(blob);

      case GenerationType.SEARCH:
        const searchRes = await ai.models.generateContent({
          model: 'gemini-3-flash-preview',
          contents: prompt,
          config: { tools: [{ googleSearch: {} }] }
        });
        return searchRes.text;

      case GenerationType.TEXT:
      default:
        const textRes = await ai.models.generateContent({
          model: 'gemini-3-flash-preview',
          contents: prompt,
          config: {
              systemInstruction: "You are a world-class e-commerce copywriter. Create high-converting content."
          }
        });
        return textRes.text;
    }
  } catch (error) {
    console.error("Gemini API Error:", error);
    return mockData(type); // Fallback for demo environments
  }
};

const mockData = (type: GenerationType) => {
    switch(type) {
        case GenerationType.IMAGE: return "https://picsum.photos/800/450";
        case GenerationType.VIDEO: return "https://www.w3schools.com/html/mov_bbb.mp4";
        case GenerationType.SEARCH: return "Our market analysis shows a 15% increase in demand for eco-friendly tech accessories. Competitors like BrandX have recently dropped prices, suggesting a saturated entry-level market.";
        default: return "Transform your daily routine with the all-new AeroStream Headphones. Engineered for silence, designed for comfort. Experience the future of sound with active noise cancellation and 40-hour battery life. Order now and elevate your audio experience.";
    }
}
