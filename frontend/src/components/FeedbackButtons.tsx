import React, { useState } from 'react';
import { ThumbsUp, ThumbsDown } from 'lucide-react';

interface FeedbackButtonsProps {
  onFeedback: (isPositive: boolean) => void;
  taskId: string;
  apiBase: string; // Add this prop
}

const FeedbackButtons: React.FC<FeedbackButtonsProps> = ({ onFeedback, taskId, apiBase }) => {
  const [feedback, setFeedback] = useState<boolean | null>(null);
  const [showFeedbackAlert, setShowFeedbackAlert] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [alertMessage, setAlertMessage] = useState('');

  const handleFeedback = async (newFeedback: boolean) => {
    if (isSubmitting) return;
    setIsSubmitting(true);
    
    try {
      const isRemoving = feedback === newFeedback;
      const payload = {
        task_id: taskId,
        is_positive: newFeedback,
        remove: isRemoving
      };
      
      console.log('Sending feedback payload:', payload);
      console.log('Sending to URL:', `${apiBase}/feedback`);
      
      const response = await fetch(`${apiBase}/feedback`, {
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
      
      const newFeedbackState = isRemoving ? null : newFeedback;
      setFeedback(newFeedbackState);
      if (newFeedbackState !== null) {
        onFeedback(newFeedbackState);
      }

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