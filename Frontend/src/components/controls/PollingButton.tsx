import Button from '@/components/controls/Button';
import { motion, useAnimation } from 'motion/react';
import { JSX, useEffect, useState, useRef } from 'react';
import { useTranslation } from 'react-i18next';

/**
 * Props for the PollingButton component
 * @interface PollingButtonProps
 */
interface PollingButtonProps {
  /** Callback function to execute on each poll interval */
  onPoll: () => void;
  /** Optional click handler for additional click behavior */
  onClick?: () => void;
  /** Whether the button is disabled */
  disabled?: boolean;
  /** Polling interval in milliseconds */
  interval?: number;
  /** Additional CSS classes to apply to the button */
  className?: string;
  /** Optional external control of polling active state. When provided, isPolling state is controlled externally */
  active?: boolean;
  /** Callback when polling state changes (for controlled components) */
  onActiveChange?: (active: boolean) => void;
}

/**
 * A button component that implements polling functionality with a visual progress indicator
 * @param {PollingButtonProps} props - The component props
 * @returns {JSX.Element} A button with polling capabilities and visual feedback
 */
export default function PollingButton({
  onPoll,
  onClick,
  disabled = false,
  interval = 3000,
  className = '',
  active,
  onActiveChange
}: PollingButtonProps): JSX.Element {
  const { t } = useTranslation();
  // Track polling state (internal state used when active prop is undefined)
  const [internalIsPolling, setInternalIsPolling] = useState<boolean>(false);
  
  // Use ref to track component mounted state
  const isMounted = useRef(false);

  // Determine if we're using controlled or uncontrolled behavior
  const isControlled = active !== undefined;
  // Use the appropriate polling state based on whether we're controlled or not
  const isPolling = isControlled ? active : internalIsPolling;

  // Animation controller for the progress bar
  const controls = useAnimation();

  /**
   * Handles the polling logic
   */
  const poll = () => {
    if (!isMounted.current) return;
    
    onPoll();
    if (isMounted.current && isPolling) {
      startPollingAnimation();
    }
  };

  /**
   * Initiates the polling animation sequence
   * Creates an animation that triggers the poll on completion
   */
  const startPollingAnimation = () => {
    if (!isMounted.current) return;
    
    controls.set({ scaleX: 0 });
    controls.start({
      scaleX: 1,
      transition: {
        duration: interval / 1000,
        ease: 'linear',
        onComplete: poll
      }
    });
  };

  /**
   * Manages the polling lifecycle
   * Starts/stops polling based on isPolling state
   */
  useEffect(() => {
    isMounted.current = true;

    if (isPolling) {
      // Initial poll when starting
      onPoll();
      // Then start the animation for the next poll
      startPollingAnimation();
    } else {
      controls.stop();
    }

    // Cleanup animation on unmount or when polling stops
    return () => {
      isMounted.current = false;
      controls.stop();
    };
  }, [isPolling, interval]);

  /**
   * Handles button click events
   * Toggles polling state and triggers optional click handler
   */
  const handleClick = () => {
    // Toggle the polling state
    const newPollingState = !isPolling;

    // For controlled components, notify parent of state change
    if (isControlled && onActiveChange) {
      onActiveChange(newPollingState);
    } else {
      // For uncontrolled components, manage state internally
      setInternalIsPolling(newPollingState);
    }

    // Call optional click handler
    onClick?.(); // Optional chaining for cleaner code
  };

  return (
    <Button
      type="button"
      size="sm"
      variant="default"
      onClick={handleClick}
      disabled={disabled}
      className={`relative overflow-hidden ${className}`}
    >
      {isPolling ? t('common.polling.stop') : t('common.polling.start')}
      {isPolling && (
        <motion.div
          className="absolute bottom-0 left-0 right-0 h-1 bg-gray-100/50"
          initial={{ scaleX: 0 }}
          animate={controls}
          style={{ originX: 0 }}
        />
      )}
    </Button>
  );
}
