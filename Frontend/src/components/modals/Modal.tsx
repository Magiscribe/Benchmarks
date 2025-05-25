import { Icon } from '@iconify/react';
import { Dialog, DialogPanel, DialogTitle, Transition, TransitionChild } from '@headlessui/react';
import { Fragment } from 'react';
import clsx from 'clsx';

/**
 * Props for the CustomModal component
 * @interface Props
 */
interface Props {
  /** Title text displayed at the top of the modal */
  title: string;
  /** Content to be displayed in the modal body */
  children: React.ReactNode;
  /** Optional buttons to be displayed at the bottom of the modal */
  buttons?: React.ReactNode;
  /** Controls the width of the modal. Defaults to 'md' */
  size?: 'sm' | 'md' | 'lg' | 'xl' | '2xl' | '3xl' | '4xl' | '5xl' | '6xl' | '7xl' | '8xl';
  /** Whether the modal is visible or not */
  open: boolean;
  /** Function to call when the modal should be closed */
  onClose: () => void;
  /** Optional background color class for the modal. Defaults to 'bg-white' */
  backgroundColor?: string;
}

/**
 * A customizable modal dialog component
 *
 * @param {Props} props - The component props
 * @returns {JSX.Element} The rendered modal component
 */
export default function CustomModal(props: Props) {
  /**
   * Handles the modal close action
   */
  function closeModal() {
    props.onClose();
  }

  /**
   * Maps size string values to corresponding Tailwind CSS classes
   */
  const sizeClassMap = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-lg',
    xl: 'max-w-xl',
    '2xl': 'max-w-2xl',
    '3xl': 'max-w-3xl',
    '4xl': 'max-w-4xl',
    '5xl': 'max-w-5xl',
    '6xl': 'max-w-6xl',
    '7xl': 'max-w-7xl',
    '8xl': 'max-w-8xl'
  };
  const sizeClass = sizeClassMap[props.size ?? 'md'];
  const backgroundColor = props.backgroundColor ?? 'bg-gray-100 dark:bg-gray-800';
  const textColor = 'text-gray-700 dark:text-gray-200';

  return (
    <Transition appear show={props.open} as={Fragment}>
      <Dialog as="div" className={clsx('fixed z-40', textColor)} onClose={closeModal}>
        <TransitionChild
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-50"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black/50 backdrop-filter transition-opacity" />
        </TransitionChild>

        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4 text-center">
            <TransitionChild
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <DialogPanel
                className={`w-full ${sizeClass} transform rounded-2xl ${backgroundColor} p-6 text-left align-middle shadow-xl transition-all`}
              >
                <DialogTitle as="h3" className="text-2xl font-medium leading-6 mb-6">
                  {props.title}
                  <button
                    className="fixed top-2 right-4 p-4 transition-colors duration-150"
                    onClick={closeModal}
                  >
                    <Icon icon="material-symbols:close-rounded" className="w-4 h-4" />
                  </button>
                </DialogTitle>
                <div className="mt-2">{props.children}</div>
                <div className="mt-4 flex justify-between">{props.buttons}</div>
              </DialogPanel>
            </TransitionChild>
          </div>
        </div>
      </Dialog>
    </Transition>
  );
}
