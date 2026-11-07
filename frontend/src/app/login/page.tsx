'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Shield, Lock, Eye, EyeOff, KeyRound, CheckCircle2, ArrowLeft } from 'lucide-react';
import { api } from '@/lib/api';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import toast from 'react-hot-toast';

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<{ email?: string; password?: string; mfa?: string }>({});

  // 2FA state
  const [mfaTicket, setMfaTicket] = useState<string | null>(null);
  const [totpCode, setTotpCode] = useState('');
  const [useRecovery, setUseRecovery] = useState(false);
  const [recoveryCode, setRecoveryCode] = useState('');

  const validateLogin = () => {
    const newErrors: typeof errors = {};
    if (!email) newErrors.email = 'Email is required';
    else if (!/\S+@\S+\.\S+/.test(email)) newErrors.email = 'Invalid email format';
    if (!password) newErrors.password = 'Password is required';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateLogin()) return;

    setLoading(true);
    try {
      const data = await api.login(email, password);
      if (data.mfa_required) {
        setMfaTicket(data.mfa_ticket);
        toast('Two-Factor Authentication required. Please enter your code.', { icon: '🔐' });
        return;
      }
      api.setToken(data.access_token);
      toast.success('Welcome back!');
      router.push('/dashboard');
    } catch (error: any) {
      // Demo auto-registration fallback if unknown email
      if (error?.response?.status === 401) {
        try {
          const name = email.split('@')[0].replace(/[._-]+/g, ' ').trim() || 'Demo User';
          const regData = await api.register({ email, password, name });
          api.setToken(regData.access_token);
          toast.success('Account created and signed in!');
          router.push('/dashboard');
          return;
        } catch {
          // Fall through to regular error reporting
        }
      }
      const errorMessage = error.response?.data?.detail
        ? Array.isArray(error.response.data.detail)
          ? error.response.data.detail.map((x: any) => x.msg).join(', ')
          : error.response.data.detail
        : 'Invalid email or password';
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleMfaVerifySubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!mfaTicket) return;

    if (!useRecovery && (!totpCode || totpCode.trim().length !== 6)) {
      setErrors({ mfa: 'Please enter a valid 6-digit verification code' });
      return;
    }
    if (useRecovery && !recoveryCode.trim()) {
      setErrors({ mfa: 'Please enter your recovery code' });
      return;
    }

    setLoading(true);
    setErrors({});
    try {
      const res = await api.verifyMfa(
        mfaTicket,
        useRecovery ? undefined : totpCode.trim(),
        useRecovery ? recoveryCode.trim() : undefined
      );
      api.setToken(res.access_token);
      toast.success(res.recovery_code_used ? 'Signed in using backup recovery code' : 'Two-factor authentication verified!');
      router.push('/dashboard');
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Invalid authentication code or expired session';
      setErrors({ mfa: msg });
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-primary-50 to-white flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <Link href="/" className="inline-flex items-center gap-2 mb-6">
            <Shield className="h-10 w-10 text-primary-600" />
            <span className="text-2xl font-bold text-gray-900">Tax Shield</span>
          </Link>
          <h1 className="text-3xl font-bold text-gray-900">
            {mfaTicket ? 'Two-Factor Challenge' : 'Welcome back'}
          </h1>
          <p className="mt-2 text-gray-600">
            {mfaTicket
              ? 'Enter the security code from your authenticator app'
              : 'Sign in to your practice and compliance workspace'}
          </p>
        </div>

        <div className="card p-6 sm:p-8 shadow-md rounded-xl bg-white border border-gray-100">
          {!mfaTicket ? (
            /* Standard Password Form */
            <form onSubmit={handleLoginSubmit} className="space-y-5">
              <Input
                label="Email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                error={errors.email}
                placeholder="ca@example.com"
                autoComplete="email"
                required
              />

              <div className="relative">
                <Input
                  label="Password"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  error={errors.password}
                  placeholder="••••••••"
                  autoComplete="current-password"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-[38px] text-gray-400 hover:text-gray-600"
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                </button>
              </div>

              <div className="flex items-center justify-between text-sm">
                <label className="flex items-center gap-2">
                  <input type="checkbox" className="rounded border-gray-300 text-primary-600 focus:ring-primary-500" />
                  <span className="text-gray-600">Remember me</span>
                </label>
                <Link href="/auth/reset" className="text-primary-600 hover:text-primary-700 font-medium">
                  Forgot password?
                </Link>
              </div>

              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? 'Signing in...' : 'Sign in'}
              </Button>
            </form>
          ) : (
            /* 2FA Challenge Form */
            <form onSubmit={handleMfaVerifySubmit} className="space-y-5">
              <div className="flex items-center justify-center p-3 bg-primary-50 rounded-lg text-primary-700 text-sm gap-2">
                <Lock className="w-4 h-4 text-primary-600 shrink-0" />
                <span>Account protected by Two-Factor Authentication</span>
              </div>

              {!useRecovery ? (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    6-Digit Authenticator Code
                  </label>
                  <input
                    type="text"
                    inputMode="numeric"
                    pattern="[0-9]*"
                    maxLength={6}
                    autoFocus
                    value={totpCode}
                    onChange={(e) => setTotpCode(e.target.value.replace(/\D/g, ''))}
                    placeholder="123456"
                    className="w-full text-center text-2xl tracking-[0.4em] font-mono py-3 px-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  />
                  {errors.mfa && <p className="mt-1 text-sm text-red-600">{errors.mfa}</p>}
                </div>
              ) : (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Emergency Backup Recovery Code
                  </label>
                  <input
                    type="text"
                    autoFocus
                    value={recoveryCode}
                    onChange={(e) => setRecoveryCode(e.target.value.toUpperCase())}
                    placeholder="7A8B-9C0D"
                    className="w-full text-center text-lg font-mono py-2.5 px-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 uppercase"
                  />
                  <p className="mt-1 text-xs text-gray-500">
                    Each backup code can only be used once.
                  </p>
                  {errors.mfa && <p className="mt-1 text-sm text-red-600">{errors.mfa}</p>}
                </div>
              )}

              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? 'Verifying Code...' : 'Verify & Complete Sign In'}
              </Button>

              <div className="flex items-center justify-between text-xs pt-2">
                <button
                  type="button"
                  onClick={() => {
                    setUseRecovery(!useRecovery);
                    setErrors({});
                  }}
                  className="text-primary-600 hover:text-primary-700 font-medium inline-flex items-center gap-1"
                >
                  <KeyRound className="w-3.5 h-3.5" />
                  {useRecovery ? 'Use 6-digit Authenticator app code' : 'Lost device? Use recovery code'}
                </button>

                <button
                  type="button"
                  onClick={() => {
                    setMfaTicket(null);
                    setTotpCode('');
                    setRecoveryCode('');
                    setErrors({});
                  }}
                  className="text-gray-500 hover:text-gray-700 inline-flex items-center gap-1"
                >
                  <ArrowLeft className="w-3 h-3" />
                  Back
                </button>
              </div>
            </form>
          )}

          <div className="mt-6 text-center text-sm text-gray-600">
            Don&apos;t have an account?{' '}
            <Link href="/register" className="text-primary-600 hover:text-primary-700 font-medium">
              Create an account
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
