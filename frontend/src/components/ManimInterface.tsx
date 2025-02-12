'use client';

import React, { useState } from 'react';

export function ManimInterface() {
  const [userPrompt, setUserPrompt] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [generatedCode, setGeneratedCode] = useState('');
  const [videoUrl, setVideoUrl] = useState('');
  const [error, setError] = useState('');

  const API_BASE = 'http://localhost:8000';
  
  const pollStatus = async (taskId: string) => {
    const response = await fetch(`${API_BASE}/status/${taskId}`);
    if (!response.ok) throw new Error('Failed to get generation status');
    return response.json();
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setVideoUrl('');

    try {
      // Start generation process
      const response = await fetch(`${API_BASE}/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt: userPrompt }),
      });

      if (!response.ok) throw new Error('Failed to start generation');
      const { task_id, code } = await response.json();
      setGeneratedCode(code);

      // Poll for results
      while (true) {
        await new Promise(resolve => setTimeout(resolve, 1000));
        const status = await pollStatus(task_id);
        
        if (status.status === 'completed' && status.video_url) {
          // Construct full URL from API_BASE and relative path
          setVideoUrl(`${API_BASE}${status.video_url}`);
          break;
        } else if (status.status === 'failed') {
          throw new Error(status.error || 'Generation failed');
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate animation');
      console.error('Error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-4">
      <div className="bg-white shadow rounded-lg p-6">
        <h1 className="text-2xl font-bold mb-4">Manim Animation Generator</h1>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <textarea
              value={userPrompt}
              onChange={(e) => setUserPrompt(e.target.value)}
              placeholder="Describe the animation you want to create..."
              className="w-full h-32 p-2 border rounded-md"
              required
            />
          </div>
          <button 
            type="submit" 
            disabled={isLoading || !userPrompt.trim()}
            className="w-full bg-blue-500 text-white p-2 rounded-md hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Generating...' : 'Generate Animation'}
          </button>
        </form>

        {error && (
          <div className="mt-4 p-4 bg-red-50 text-red-600 rounded-md">
            {error}
          </div>
        )}

        {generatedCode && (
          <div className="mt-4">
            <h3 className="font-semibold mb-2">Generated Manim Code:</h3>
            <pre className="bg-gray-100 p-4 rounded-md overflow-x-auto">
              <code>{generatedCode}</code>
            </pre>
          </div>
        )}

        {videoUrl && (
          <div className="mt-4">
            <h3 className="font-semibold mb-2">Generated Animation:</h3>
            <div className="relative w-full pt-[56.25%] bg-gray-100 rounded-md">
              <video
                key={videoUrl} // Force video reload when URL changes
                src={videoUrl}
                controls
                className="absolute top-0 left-0 w-full h-full rounded-md"
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}