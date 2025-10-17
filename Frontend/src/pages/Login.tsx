import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Eye, EyeOff, Mail, Lock } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import lawgptLogo from "@/assets/lawgpt-logo.png";
import ashokaChakra from "@/assets/ashoka-chakra.png";

const Login = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();
  setIsLoading(true);

  try {
    const response = await fetch("http://localhost:5000/api/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    const data = await response.json();
    setIsLoading(false);

    if (response.ok && data.message) {
      toast({
        title: "OTP Sent!",
        description: "Enter the code sent to your email.",
      });
      navigate("/otp-verification", { state: { email, purpose: "login" } });
    } else {
      toast({
        title: "Error",
        description: data.error || "Invalid credentials",
        variant: "destructive",
      });
    }
  } catch (err) {
    setIsLoading(false);
    toast({
      title: "Error",
      description: "Something went wrong. Please try again.",
      variant: "destructive",
    });
  }
};

  return (
    <div className="min-h-screen bg-cream flex items-center justify-center p-4 relative overflow-hidden">
      {/* Bright Ashoka Chakra Background */}
      <div
        className="absolute inset-0 flex items-center justify-center opacity-10"
        style={{
          backgroundImage: `url(${ashokaChakra})`,
          backgroundSize: "60%",
          backgroundPosition: "center",
          backgroundRepeat: "no-repeat",
        }}
      >
        <img
          src={ashokaChakra}
          alt=""
          className="w-1/2 h-auto animate-spin-slow"
          style={{ filter: "brightness(1.5)" }}
        />
      </div>

      <div className="w-full max-w-md relative z-10 animate-scale-in">
        <div className="bg-white rounded-2xl shadow-gold p-8 border-2 border-gold/20">
          {/* Logo */}
          <div className="text-center mb-8">
            <img src={lawgptLogo} alt="LawGPT" className="w-20 h-20 mx-auto mb-4" />
            <h1 className="text-3xl font-bold text-primary">Welcome Back</h1>
            <div className="w-20 h-1 bg-gold mx-auto mt-3"></div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Email Field */}
            <div className="space-y-2">
              <Label htmlFor="email" className="text-primary flex items-center gap-2">
                <Mail className="w-4 h-4" />
                Email Address
              </Label>
              <div className="relative">
                <Input
                  id="email"
                  type="email"
                  placeholder="your.email@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="pl-4 focus:ring-gold focus:border-gold transition-smooth"
                  required
                />
              </div>
            </div>

            {/* Password Field */}
            <div className="space-y-2">
              <Label htmlFor="password" className="text-primary flex items-center gap-2">
                <Lock className="w-4 h-4" />
                Password
              </Label>
              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="pr-10 focus:ring-gold focus:border-gold transition-smooth"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-primary transition-smooth"
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>

            {/* Remember Me & Forgot Password */}
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="remember"
                  checked={rememberMe}
                  onCheckedChange={(checked) => setRememberMe(checked as boolean)}
                  className="border-gold data-[state=checked]:bg-gold data-[state=checked]:border-gold"
                />
                <label
                  htmlFor="remember"
                  className="text-sm text-muted-foreground cursor-pointer hover:text-primary transition-smooth"
                >
                  Remember me
                </label>
              </div>
              <button
                type="button"
                className="text-sm text-gold hover:text-gold/80 transition-smooth font-medium"
                // You can add forgot password logic here
              >
                Forgot Password?
              </button>
            </div>

            {/* Submit Button */}
            <Button
              type="submit"
              className="w-full bg-gold hover:bg-gold/90 text-primary font-semibold py-6 text-lg shadow-gold transition-smooth"
              disabled={isLoading}
            >
              {isLoading ? (
                <span className="flex items-center gap-2">
                  <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                      fill="none"
                    />
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    />
                  </svg>
                  Signing in...
                </span>
              ) : (
                "Sign In"
              )}
            </Button>
          </form>

          {/* Sign Up Link */}
          <div className="mt-6 text-center">
            <p className="text-muted-foreground">
              Don't have an account?{" "}
              <Link
                to="/signup"
                className="text-gold hover:text-gold/80 font-semibold transition-smooth"
              >
                Sign Up
              </Link>
            </p>
          </div>
        </div>

        {/* Back to Home */}
        <div className="text-center mt-6">
          <button
            onClick={() => navigate("/")}
            className="text-primary hover:text-gold transition-smooth"
          >
            ← Back to Home
          </button>
        </div>
      </div>
    </div>
  );
};

export default Login;
