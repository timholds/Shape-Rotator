'use client';

import React, { useState, useEffect } from 'react';
import FeedbackButtons from './FeedbackButtons';
import styles from './ManimInterface.module.css';

type GenerationStep = 'idle' | 'generating-code' | 'rendering-video' | 'completed';

export function ManimInterface() {
  const [userPrompt, setUserPrompt] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [generatedCode, setGeneratedCode] = useState('');
  const [videoUrl, setVideoUrl] = useState('');
  const [error, setError] = useState('');
  const [currentStep, setCurrentStep] = useState<GenerationStep>('idle');
  const [currentGenerationId, setCurrentGenerationId] = useState<string | null>(null);
  const [apiBase, setApiBase] = useState('');

  useEffect(() => {
    setApiBase(
      process.env.NEXT_PUBLIC_API_URL || 
      (typeof window !== 'undefined' 
        ? `${window.location.protocol}//${window.location.hostname}:8000`
        : 'http://localhost:8000')
    );
  }, []);

  const getProgressPercentage = (step: GenerationStep) => {
    switch (step) {
      case 'idle': return 0;
      case 'generating-code': return 33;
      case 'rendering-video': return 66;
      case 'completed': return 100;
      default: return 0;
    }
  };

  const getProgressText = (step: GenerationStep) => {
    switch (step) {
      case 'idle': return 'Ready to generate';
      case 'generating-code': return 'Generating Manim code...';
      case 'rendering-video': return 'Rendering animation...';
      case 'completed': return 'Generation complete!';
      default: return '';
    }
  };

  const handleFeedback = (isPositive: boolean) => {
    console.log(`Feedback received: ${isPositive ? 'positive' : 'negative'} for generation ${currentGenerationId}`);
  };

  const pollStatus = async (taskId: string) => {
    const response = await fetch(`${apiBase}/status/${taskId}`);
    if (!response.ok) throw new Error('Failed to get generation status');
    const status = await response.json();
    
    if (status.code && !generatedCode) {
      setGeneratedCode(status.code);
      setCurrentStep('rendering-video');
    }
    
    return status;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!apiBase) return;
    
    setIsLoading(true);
    setError('');
    setVideoUrl('');
    setGeneratedCode('');
    setCurrentStep('generating-code');
    setCurrentGenerationId(null);

    try {
      const response = await fetch(`${apiBase}/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          prompt: userPrompt,
          options: {
            quality: "low",
            resolution: "720p"
          }
        }),
      });

      if (!response.ok) throw new Error('Failed to start generation');
      const { task_id } = await response.json();
      
      setCurrentGenerationId(task_id);

      while (true) {
        await new Promise(resolve => setTimeout(resolve, 1000));
        const status = await pollStatus(task_id);
        
        if (status.status === 'completed' && status.video_url) {
          setVideoUrl(`${apiBase}${status.video_url}`);
          setCurrentStep('completed');
          break;
        } else if (status.status === 'failed') {
          throw new Error(status.error || 'Generation failed');
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate animation');
      console.error('Error:', err);
      setCurrentStep('idle');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <h1 className={styles.title}>Manim Animation Generator</h1>
        
        <form onSubmit={handleSubmit} className={styles.form}>
          <div className="w-full">
            <textarea
              value={userPrompt}
              onChange={(e) => setUserPrompt(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  if (userPrompt.trim() && !isLoading) {
                    handleSubmit(e);
                  }
                }
              }}
              placeholder="Describe the animation you want to create..."
              className={styles.textarea}
              required
            />
          </div>
          <button 
            type="submit" 
            disabled={isLoading || !userPrompt.trim()}
            className={styles.button}
          >
            {isLoading ? 'Generating...' : 'Generate Animation'}
          </button>
        </form>

        {error && (
          <div className={styles.error}>{error}</div>
        )}

        {isLoading && (
          <div className={styles.progressContainer}>
            <div className={styles.progressText}>
              <span>{getProgressText(currentStep)}</span>
              <span>{getProgressPercentage(currentStep)}%</span>
            </div>
            <div className={styles.progressBar}>
              <div 
                className={styles.progressFill}
                style={{ width: `${getProgressPercentage(currentStep)}%` }}
              />
            </div>
          </div>
        )}

        {videoUrl && (
          <div className={styles.videoContainer}>
            <h3 className={styles.videoTitle}>Generated Animation:</h3>
            <div className={styles.videoWrapper}>
              <video
                key={videoUrl}
                src={videoUrl}
                controls
                className={styles.video}
              />
            </div>
            {currentGenerationId && (
              <div className="mt-4">
                <FeedbackButtons 
                  taskId={currentGenerationId}
                  onFeedback={handleFeedback}
                />
              </div>
            )}
          </div>
        )}

        {generatedCode && (
          <div className={styles.codeContainer}>
            <h3 className={styles.videoTitle}>Generated Manim Code:</h3>
            <pre className={styles.codeBlock}>
              <code className={styles.codeText}>{generatedCode}</code>
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}