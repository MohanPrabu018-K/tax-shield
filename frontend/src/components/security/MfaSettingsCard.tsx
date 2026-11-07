'use client';

import React, { useState, useEffect } from 'react';
import Image from 'next/image';
import { ShieldCheck, ShieldAlert, Key, QrCode, Copy, Check, RefreshCw, AlertTriangle, Eye, EyeOff } from 'lucide-react';
import { api } from '@/lib/api';
import { Button } from '@/components/ui/Button';
import toast from 'react-hot-toast';

export function MfaSettingsCard() {
  const [loading, setLoading] = useState(true);
  const [mfaEnabled, setMfaEnabled] = useState(false);
  const [remainingCodes, setRemainingCodes] = useState(0);

  // Setup modal / state
  const [isSettingUp, setIsSettingUp] = useState(false);
  const [setupData, setSetupData] = useState<{
    secret: string;
    qr_code: string;
    recovery_codes: string[];
    provisioning_uri: string;
  } | null>(null);
  const [verifyCode, setVerifyCode] = useState('');
  const [enabling, setEnabling] = useState(false);
  const [copiedSecret, setCopiedSecret] = useState(false);

  // Disable state
  const [isDisabling, setIsDisabling] = useState(false);
  const [disablePassword, setDisablePassword] = useState('');
  const [disableCode, setDisableCode] = useState('');
  const [disabling, setDisabling] = useState(false);

  const loadStatus = async () => {
    try {
      setLoading(true);
      const res = await api.getMfaStatus();
      setMfaEnabled(res.mfa_enabled);
      setRemainingCodes(res.recovery_codes_remaining || 0);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStatus();
  }, []);

  const handleStartSetup = async () => {
    try {
      setLoading(true);
      const data = await api.setupMfa();
      setSetupData(data);
      setIsSettingUp(true);
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to start MFA setup');
    } finally {
      setLoading(false);
    }
  };

  const handleConfirmEnable = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!verifyCode || verifyCode.trim().length !== 6) {
      toast.error('Please enter the 6-digit code shown in your app');
      return;
    }
    try {
      setEnabling(true);
      await api.enableMfa(verifyCode.trim());
      toast.success('Two-Factor Authentication is now enabled!');
      setIsSettingUp(false);
      setSetupData(null);
      setVerifyCode('');
      await loadStatus();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Invalid verification code');
    } finally {
      setEnabling(false);
    }
  };

  const handleConfirmDisable = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!disablePassword) {
      toast.error('Account password is required');
      return;
    }
    try {
      setDisabling(true);
      const res = await api.disableMfa(disablePassword, disableCode ? disableCode.trim() : undefined);
      if (res.access_token) {
        api.setToken(res.access_token);
      }
      toast.success('Two-Factor Authentication disabled');
      setIsDisabling(false);
      setDisablePassword('');
      setDisableCode('');
      await loadStatus();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to disable MFA. Check your password.');
    } finally {
      setDisabling(false);
    }
  };

  if (loading && !isSettingUp && !isDisabling) {
    return (
      <div className="card p-6 bg-white border border-gray-200 rounded-xl animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
        <div className="h-4 bg-gray-100 rounded w-2/3"></div>
      </div>
    );
  }

  return (
    <div className="card p-6 bg-white border border-gray-200 rounded-xl shadow-sm">
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <div className={`p-2.5 rounded-lg ${mfaEnabled ? 'bg-emerald-50 text-emerald-600' : 'bg-amber-50 text-amber-600'}`}>
            {mfaEnabled ? <ShieldCheck className="w-6 h-6" /> : <ShieldAlert className="w-6 h-6" />}
          </div>
          <div>
            <h3 className="text-base font-semibold text-gray-900">
              Two-Factor Authentication (MFA / 2FA)
            </h3>
            <p className="text-sm text-gray-500 mt-0.5">
              Secure practice and client accounts with RFC 6238 TOTP authenticator app tokens.
            </p>
          </div>
        </div>

        <div>
          {mfaEnabled ? (
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-600"></span>
              Active Protection
            </span>
          ) : (
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-amber-100 text-amber-800">
              <span className="w-1.5 h-1.5 rounded-full bg-amber-600"></span>
              Recommended
            </span>
          )}
        </div>
      </div>

      {!isSettingUp && !isDisabling && (
        <div className="mt-5 pt-4 border-t border-gray-100 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="text-xs text-gray-500">
            {mfaEnabled ? (
              <span>
                Standard TOTP active. <strong>{remainingCodes}</strong> emergency backup recovery codes remaining.
              </span>
            ) : (
              <span>
                Protects client financial records, audit workpapers, and banking data from unauthorized credential access.
              </span>
            )}
          </div>

          <div className="flex items-center gap-2">
            {mfaEnabled ? (
              <Button
                variant="secondary"
                size="sm"
                onClick={() => setIsDisabling(true)}
                className="text-red-600 hover:text-red-700 hover:bg-red-50 border-red-200"
              >
                Disable 2FA
              </Button>
            ) : (
              <Button size="sm" onClick={handleStartSetup}>
                Set up Authenticator App
              </Button>
            )}
          </div>
        </div>
      )}

      {/* Setup View */}
      {isSettingUp && setupData && (
        <div className="mt-6 pt-5 border-t border-gray-200 space-y-6">
          <div className="p-4 bg-primary-50 rounded-lg text-primary-900 text-sm">
            <h4 className="font-semibold mb-1">Step 1: Scan with Authenticator App</h4>
            <p className="text-xs text-primary-700">
              Use Google Authenticator, Microsoft Authenticator, Apple Passwords, or 1Password.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-center">
            <div className="flex flex-col items-center p-4 bg-gray-50 rounded-xl border border-gray-200">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={setupData.qr_code}
                alt="Authenticator QR Code"
                className="w-44 h-44 rounded-lg shadow-inner bg-white p-2"
              />
              <span className="text-xs text-gray-500 mt-2">Scan QR code in app</span>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-1">
                  Manual Entry Secret Key
                </label>
                <div className="flex items-center gap-2">
                  <code className="text-xs font-mono bg-gray-100 p-2 rounded border border-gray-200 text-gray-800 break-all select-all flex-1">
                    {setupData.secret}
                  </code>
                  <button
                    type="button"
                    onClick={() => {
                      navigator.clipboard.writeText(setupData.secret);
                      setCopiedSecret(true);
                      setTimeout(() => setCopiedSecret(false), 2000);
                    }}
                    className="p-2 border border-gray-200 rounded hover:bg-gray-50 text-gray-600"
                    title="Copy Secret"
                  >
                    {copiedSecret ? <Check className="w-4 h-4 text-emerald-600" /> : <Copy className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-1">
                  Emergency Recovery Codes (Save Securely)
                </label>
                <div className="grid grid-cols-2 gap-1.5 p-2.5 bg-gray-50 rounded border border-gray-200 font-mono text-xs text-gray-700 select-all">
                  {setupData.recovery_codes.map((code, idx) => (
                    <div key={idx} className="tracking-wider">
                      {code}
                    </div>
                  ))}
                </div>
                <p className="text-[11px] text-gray-500 mt-1">
                  Store these in a safe place. They allow access if you lose your mobile phone.
                </p>
              </div>
            </div>
          </div>

          <form onSubmit={handleConfirmEnable} className="pt-4 border-t border-gray-100 space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-800 mb-1">
                Step 2: Enter the 6-Digit Code Generated by Your App
              </label>
              <div className="flex gap-3 max-w-xs">
                <input
                  type="text"
                  maxLength={6}
                  value={verifyCode}
                  onChange={(e) => setVerifyCode(e.target.value.replace(/\D/g, ''))}
                  placeholder="123456"
                  className="font-mono text-lg text-center tracking-widest py-2 px-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                  autoFocus
                />
                <Button type="submit" disabled={enabling}>
                  {enabling ? 'Verifying...' : 'Activate MFA'}
                </Button>
              </div>
            </div>

            <button
              type="button"
              onClick={() => {
                setIsSettingUp(false);
                setSetupData(null);
              }}
              className="text-xs text-gray-500 hover:text-gray-700 underline"
            >
              Cancel setup
            </button>
          </form>
        </div>
      )}

      {/* Disable View */}
      {isDisabling && (
        <form onSubmit={handleConfirmDisable} className="mt-6 pt-5 border-t border-gray-200 space-y-4 max-w-md">
          <div className="flex items-center gap-2 text-sm text-red-600 bg-red-50 p-3 rounded-lg">
            <AlertTriangle className="w-5 h-5 shrink-0" />
            <span>Disabling 2FA will remove extra protection from your account and revoke other active sessions.</span>
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-1">Account Password (Re-authentication)</label>
            <input
              type="password"
              value={disablePassword}
              onChange={(e) => setDisablePassword(e.target.value)}
              placeholder="Your password"
              className="w-full text-sm py-2 px-3 border border-gray-300 rounded-lg"
              required
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-1">Current 6-Digit Code (or Recovery Code)</label>
            <input
              type="text"
              value={disableCode}
              onChange={(e) => setDisableCode(e.target.value)}
              placeholder="123456 or 7A8B-9C0D"
              className="w-full text-sm py-2 px-3 border border-gray-300 rounded-lg font-mono"
            />
          </div>

          <div className="flex items-center gap-2 pt-2">
            <Button type="submit" variant="danger" disabled={disabling}>
              {disabling ? 'Disabling...' : 'Confirm Disable'}
            </Button>
            <Button
              type="button"
              variant="secondary"
              onClick={() => {
                setIsDisabling(false);
                setDisablePassword('');
                setDisableCode('');
              }}
            >
              Cancel
            </Button>
          </div>
        </form>
      )}
    </div>
  );
}
