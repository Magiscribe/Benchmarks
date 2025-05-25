import remarkGfm from 'remark-gfm';
import Markdown from 'react-markdown';
import clsx from 'clsx';

const baseStyles = {
  base: 'prose max-w-none',
  layout: '[&>ul>li>ul]:pl-5 [&>ul>li>ul]:mt-1',
  images: 'prose-img:rounded-2xl',
  spacing: 'prose-code:px-1 prose-blockquote:pl-4 prose-pre:p-4 prose-ul:pl-5',
  roundedCorners: 'prose-code:rounded-sm prose-pre:rounded-lg',
  lists: 'prose-ul:list-disc'
};

const lightStyles = {
  text: 'text-slate-800 prose-headings:text-gray-900 prose-p:text-gray-700 prose-strong:text-gray-900',
  links: 'prose-a:text-blue-600 hover:prose-a:text-blue-500',
  code: 'prose-code:text-blue-600 prose-code:bg-blue-50 prose-pre:bg-gray-100',
  quotes: 'prose-blockquote:text-gray-600 prose-blockquote:border-gray-300',
  decorative: 'prose-hr:border-gray-300 prose-ul:text-gray-700 prose-li:marker:text-blue-600'
};

const darkStyles = {
  text: 'dark:text-slate-100 dark:prose-headings:text-gray-100 dark:prose-p:text-gray-300 dark:prose-strong:text-gray-100',
  links: 'dark:prose-a:text-blue-400 dark:hover:prose-a:text-blue-300',
  code: 'dark:prose-code:text-blue-300 dark:prose-code:bg-gray-800/50 dark:prose-pre:bg-gray-800/50',
  quotes: 'dark:prose-blockquote:text-gray-400 dark:prose-blockquote:border-gray-600',
  decorative:
    'dark:prose-hr:border-gray-700 dark:prose-ul:text-gray-300 dark:prose-li:marker:text-blue-400'
};

export default function CustomMarkdown({ content }: { content: string }) {
  return (
    <div
      className={clsx(
        Object.values(baseStyles),
        Object.values(lightStyles),
        Object.values(darkStyles)
      )}
    >
      <Markdown remarkPlugins={[remarkGfm]}>{content}</Markdown>
    </div>
  );
}
