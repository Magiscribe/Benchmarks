import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '@/providers/AuthProvider';
import Container from '@/components/layouts/Container';
import Loading from '@/components/Loading';
import Input from '@/components/controls/Input';
import Button from '@/components/controls/Button';
import LinkStack from '@/components/common/LinkStack';
import PageHeader from '@/components/common/PageHeader';
import Banner from '@/components/common/BannerStatus';
import { useTranslation } from 'react-i18next';

export default function Page() {
  const { t } = useTranslation();
  const [resetInput, setResetInput] = useState({
    username: '',
    newPassword: '',
    confirmationCode: ''
  });
  const [error, setError] = useState<string | undefined>();
  const [searchParams] = useSearchParams();
  const [isLoading, setIsLoading] = useState(false);

  const auth = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (searchParams.has('username')) {
      setResetInput({ ...resetInput, username: searchParams.get('username') ?? '' });
    }
  }, []);

  const resetPassword = async (event: React.MouseEvent<HTMLButtonElement>) => {
    event.preventDefault();
    setIsLoading(true);

    try {
      await auth.confirmResetPassword(resetInput);
      navigate(`/auth/sign-in`);
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      }
      console.error(JSON.stringify(err));
    } finally {
      setIsLoading(false);
    }
  };

  const authLinks = [
    {
      prefixText: t('auth.reset.newUser'),
      linkText: t('auth.reset.signUp'),
      to: '/auth/sign-up'
    },
    {
      prefixText: t('auth.reset.rememberPassword'),
      linkText: t('auth.reset.signIn'),
      to: '/auth/sign-in'
    }
  ];

  return (
    <Container>
      <PageHeader title={t('auth.reset.title')} subtitle={t('auth.reset.subtitle')} />
      <Banner type="error" message={error} />
      <form className="w-full flex flex-col">
        <Input
          fullWidth
          type="text"
          placeholder={t('auth.reset.code')}
          onChange={(e) => setResetInput({ ...resetInput, confirmationCode: e.target.value })}
        />
        <Input
          fullWidth
          type="password"
          placeholder={t('auth.reset.newPassword')}
          onChange={(e) => setResetInput({ ...resetInput, newPassword: e.target.value })}
        />
        <Button onClick={resetPassword} disabled={isLoading}>
          {isLoading ? <Loading /> : t('auth.reset.buttonText')}
        </Button>
      </form>
      <LinkStack links={authLinks} />
    </Container>
  );
}
