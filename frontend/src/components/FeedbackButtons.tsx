import React, { useState } from 'react';
import { ThumbsUp, ThumbsDown } from 'lucide-react';

const FeedbackButtons = ({ onFeedback, taskId }) => {
  const [feedback, setFeedback] = useState(null);
  const [showFeedbackAlert, setShowFeedbackAlert] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [alertMessage, setAlertMessage] = useState('');

  const handleFeedback = async (newFeedback) => {
    if (isSubmitting) return;
    setIsSubmitting(true);
    
    try {
      // If clicking the same button again, we're removing feedback
      const isRemoving = feedback === newFeedback;
      const payload = {
        task_id: taskId,
        is_positive: newFeedback,
        remove: isRemoving
      };
      
      console.log('Sending feedback payload:', payload);
      
      const response = await fetch('http://localhost:8000/feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json();
        console.error('Feedback error details:', errorData);
        throw new Error('Failed to submit feedback');
      }
      
      // Update feedback state
      const newFeedbackState = isRemoving ? null : newFeedback;
      setFeedback(newFeedbackState);
      onFeedback?.(newFeedbackState);

      // Show appropriate message
      setAlertMessage(isRemoving ? 'Feedback removed!' : 'Feedback submitted!');
      setShowFeedbackAlert(true);
      setTimeout(() => setShowFeedbackAlert(false), 3000);
      
    } catch (error) {
      console.error('Error submitting feedback:', error);
      setAlertMessage('Error submitting feedback');
      setShowFeedbackAlert(true);
      setTimeout(() => setShowFeedbackAlert(false), 3000);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="relative">
      <div className="flex items-center gap-4 mt-2">
        <span className="text-sm text-gray-600">Was this animation helpful?</span>
        <button
          onClick={() => handleFeedback(true)}
          disabled={isSubmitting}
          className={`p-2 rounded-full transition-colors ${
            feedback === true
              ? 'bg-green-100 text-green-600'
              : 'hover:bg-gray-100 text-gray-500'
          } disabled:opacity-50 disabled:cursor-not-allowed`}
          aria-label="Thumbs up"
        >
          <ThumbsUp size={20} />
        </button>
        <button
          onClick={() => handleFeedback(false)}
          disabled={isSubmitting}
          className={`p-2 rounded-full transition-colors ${
            feedback === false
              ? 'bg-red-100 text-red-600'
              : 'hover:bg-gray-100 text-gray-500'
          } disabled:opacity-50 disabled:cursor-not-allowed`}
          aria-label="Thumbs down"
        >
          <ThumbsDown size={20} />
        </button>
        {feedback !== null && (
          <span className="text-sm text-gray-600">
            {feedback ? 'Thanks for the feedback :)' : 'Thanks for the feedback :)'}
            <br />
          </span>
        )}
      </div>
      
      {showFeedbackAlert && (
        <div className="absolute bottom-4 right-4 bg-green-100 text-green-800 px-4 py-2 rounded-md shadow-md">
          {alertMessage}
        </div>
      )}
    </div>
  );
};

export default FeedbackButtons;