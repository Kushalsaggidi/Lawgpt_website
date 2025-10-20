import { useState, useRef, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import lawgptLogo from "@/assets/lawgpt-logo.png";
import ashokaChakra from "@/assets/ashoka-chakra.png";

const OtpVerification = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { toast } = useToast();
  const [otp, setOtp] = useState(["", "", "", "", "", ""]);
  const [isLoading, setIsLoading] = useState(false);
  const inputRefs = useRef([]);
  const email = location.state?.email || "your email";
  const purpose = location.state?.purpose || "signup"; // or "login"

  useEffect(() => {
    inputRefs.current[0]?.focus();
  }, []);

  const handleChange = (index, value) => {
    if (!/^\d*$/.test(value)) return;
    const newOtp = [...otp];
    newOtp[index] = value;
    setOtp(newOtp);
    if (value && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handleKeyDown = (index, e) => {
    if (e.key === "Backspace" && !otp[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  };

  const handlePaste = (e) => {
    e.preventDefault();
    const pastedData = e.clipboardData.getData("text").slice(0, 6);
    if (!/^\d+$/.test(pastedData)) return;
    const newOtp = [...otp];
    pastedData.split("").forEach((char, idx) => {
      if (idx < 6) newOtp[idx] = char;
    });
    setOtp(newOtp);
    const lastIndex = Math.min(pastedData.length, 5);
    inputRefs.current[lastIndex]?.focus();
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const otpValue = otp.join("");
    if (otpValue.length !== 6) {
      toast({
        title: "Error",
        description: "Please enter all 6 digits",
        variant: "destructive",
      });
      return;
    }
    setIsLoading(true);

    try {
      const response = await fetch("http://localhost:5000/api/verify-otp", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, otp: otpValue, purpose }),
      });
      const data = await response.json();
      setIsLoading(false);
      if (response.ok) {
        toast({
          title: "Success!",
          description: data.message || "Email verified successfully",
        });
        if (purpose === "login" && data.token) {
          localStorage.setItem("token", data.token);
          localStorage.setItem("userEmail", email);
          navigate("/dashboard");
        } else if (purpose === "signup") {
          // Optionally, redirect to login here or show further instructions!
          navigate("/login");
        }
      } else {
        toast({
          title: "Error",
          description: data.error || "Invalid or expired OTP.",
          variant: "destructive",
        });
      }
    } catch (err) {
      setIsLoading(false);
      toast({
        title: "Error",
        description: "Verification failed. Try again.",
        variant: "destructive",
      });
    }
  };

  const handleResend = async () => {
    try {
      const response = await fetch("http://localhost:5000/api/resend-otp", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, purpose }),
      });
      const data = await response.json();
      toast({
        title: "OTP Sent",
        description: data.message || "Demo OTP: " + data.otp_demo,
        duration: 8000,
      });
      setOtp(["", "", "", "", "", ""]);
      inputRefs.current[0]?.focus();
    } catch {
      toast({
        title: "Error",
        description: "Unable to resend OTP.",
        variant: "destructive",
      });
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-6">
      <div className="w-full max-w-md bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-center mb-4">
          <img src={lawgptLogo} alt="logo" className="h-10 mr-2" />
          <img src={ashokaChakra} alt="chakra" className="h-6" />
        </div>
        <h2 className="text-xl font-semibold text-center mb-2">Verify OTP</h2>
        <p className="text-sm text-center text-gray-600 mb-4">Enter the 6-digit code sent to {email}</p>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="flex justify-between space-x-2">
            {otp.map((digit, idx) => (
              <input
                key={idx}
                ref={(el) => (inputRefs.current[idx] = el)}
                value={digit}
                onChange={(e) => handleChange(idx, e.target.value)}
                onKeyDown={(e) => handleKeyDown(idx, e)}
                onPaste={idx === 0 ? handlePaste : undefined}
                type="text"
                inputMode="numeric"
                pattern="\d*"
                maxLength={1}
                className="w-10 h-12 text-center border rounded-md"
                autoComplete="one-time-code"
                title={`Digit ${idx + 1}`}
                placeholder="•"
                aria-label={`OTP digit ${idx + 1}`}
              />
            ))}
          </div>
          <div className="flex items-center justify-between">
            <Button type="submit" disabled={isLoading}>
              {isLoading ? "Verifying..." : "Verify"}
            </Button>
            <button type="button" onClick={handleResend} className="text-sm text-blue-600">
              Resend OTP
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default OtpVerification;
