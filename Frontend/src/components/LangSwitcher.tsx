import { useTranslation } from 'react-i18next';
import { JSX } from 'react';
import Select from './controls/Select';
import { getAvailableLanguages } from '@/i18n/i18n';

interface LangSwitcherProps {
  className?: string;
  sizeVariant?: 'xs' | 'sm' | 'md' | 'lg';
}

/**
 * Language switcher component that allows users to change the application language
 *
 * @component
 * @param {LangSwitcherProps} props - Component props
 * @param {string} [props.className] - Additional CSS classes
 * @param {('xs'|'sm'|'md'|'lg')} [props.size='sm'] - Size of the select component
 * @returns {JSX.Element} A dropdown for selecting language
 */
export default function LangSwitcher({
  className,
  sizeVariant = 'sm'
}: LangSwitcherProps): JSX.Element {
  const { i18n } = useTranslation();
  const languages = getAvailableLanguages();

  const changeLanguage = (lng: string) => {
    i18n.changeLanguage(lng);
  };

  return (
    <Select
      sizeVariant={sizeVariant}
      variant="minimal"
      className={className}
      onChange={(e) => changeLanguage(e.target.value)}
      value={i18n.language}
      aria-label="Select Language"
    >
      {languages.map((lang) => (
        <option key={lang} value={lang}>
          {lang.toUpperCase()}
        </option>
      ))}
    </Select>
  );
}
