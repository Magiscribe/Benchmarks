import { Icon } from '@iconify/react';
import { AnimatePresence, motion } from 'motion/react';
import { useTranslation } from 'react-i18next';

export type BannerType = 'error' | 'success' | 'info';

interface Props {
  type: BannerType;
  message?: string;
  showSupport?: boolean;
}

const bannerStyles = {
  error: {
    bg: 'bg-red-600/70 dark:bg-red-500/20',
    text: 'text-red-50 dark:text-red-400',
    icon: 'material-symbols:close-rounded'
  },
  success: {
    bg: 'bg-green-600/70 dark:bg-green-500/20',
    text: 'text-green-50 dark:text-green-400',
    icon: 'material-symbols:check-circle-outline-rounded'
  },
  info: {
    bg: 'bg-blue-600/70 dark:bg-blue-500/20',
    text: 'text-blue-50 dark:text-blue-400',
    icon: 'material-symbols:info-outline-rounded'
  }
};

export default function Banner({ type, message, showSupport = true }: Props) {
  const { t } = useTranslation();
  const styles = bannerStyles[type];

  return (
    <AnimatePresence mode="wait">
      {message && (
        <motion.div
          key={`${type}-${message}`}
          className={`${styles.bg} ${styles.text} w-full rounded-2xl p-2 px-6 my-2 -indent-2`}
          initial={{ opacity: 0, y: -30 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -30 }}
          transition={{ duration: 0.2, type: 'spring', stiffness: 100 }}
        >
          <p className="flex items-center font-bold">
            <Icon icon={styles.icon} className="-ml-1 mr-3 text-xl" />
            {t(`common.banner.${type}Title`)}
          </p>
          <p className="text-sm ml-2">{message}</p>
          {showSupport && (
            <div className="text-sm mt-1 ml-2">
              {t('common.banner.support')}{' '}
              <a
                href={`mailto:${t('site.supportEmail')}`}
                className="underline hover:text-white/80"
              >
                {t('common.banner.contact', { email: t('site.supportEmail') })}
              </a>
            </div>
          )}
        </motion.div>
      )}
    </AnimatePresence>
  );
}
