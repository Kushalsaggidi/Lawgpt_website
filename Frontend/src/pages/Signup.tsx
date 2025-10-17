import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Eye, EyeOff, Mail, Lock, User } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import lawgptLogo from "@/assets/lawgpt-logo.png";
import ashokaChakra from "@/assets/ashoka-chakra.png";

const Signup = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [agreeToTerms, setAgreeToTerms] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const getPasswordStrength = (pass) => {
    if (!pass) return { strength: 0, text: "", color: "" };
    if (pass.length < 6) return { strength: 25, text: "Weak", color: "bg-red-500" };
    if (pass.length < 10) return { strength: 50, text: "Fair", color: "bg-yellow-500" };
    if (pass.length < 14) return { strength: 75, text: "Good", color: "bg-blue-500" };
    return { strength: 100, text: "Strong", color: "bg-green-500" };
  };

  const passwordStrength = getPasswordStrength(password);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!agreeToTerms) {
      toast({
        title: "Error",
        description: "Please agree to terms and conditions",
        variant: "destructive",
      });
      return;
    }
    if (password !== confirmPassword) {
      toast({
        title: "Error",
        description: "Passwords do not match",
        variant: "destructive",
      });
      return;
    }
    setIsLoading(true);

    try {
      const response = await fetch("http://localhost:5000/api/signup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email, password }),
      });
      const data = await response.json();
      setIsLoading(false);

      if (response.ok) {
        toast({
          title: "Success!",
          description: data.message || "Signup successful. Check your email for OTP!",
          duration: 10000,
        });
        // You can pass more info if OTP verification required
        navigate("/otp-verification", { state: { email } });
      } else {
        toast({
          title: "Error",
          description: data.error || "Signup failed",
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
            <h1 className="text-3xl font-bold text-primary">Create Your Account</h1>
            <div className="w-20 h-1 bg-gold mx-auto mt-3"></div>
          </div>
          {/* Progress Step Indicator */}
          <div className="flex items-center justify-center gap-2 mb-8">
            <div className="w-8 h-8 rounded-full bg-gold text-white flex items-center justify-center font-semibold">
              1
            </div>
            <div className="w-16 h-1 bg-gold"></div>
            <div className="w-8 h-8 rounded-full bg-muted text-muted-foreground flex items-center justify-center font-semibold">
              2
            </div>
          </div>
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Name Field */}
            <div className="space-y-2">
              <Label htmlFor="name" className="text-primary flex items-center gap-2">
                <User className="w-4 h-4" />
                Full Name
              </Label>
              <Input
                id="name"
                type="text"
                placeholder="John Doe"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="focus:ring-gold focus:border-gold transition-smooth"
                required
              />
            </div>

            {/* Email Field */}
            <div className="space-y-2">
              <Label htmlFor="email" className="text-primary flex items-center gap-2">
                <Mail className="w-4 h-4" />
                Email Address
              </Label>
              <Input
                id="email"
                type="email"
                placeholder="your.email@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="focus:ring-gold focus:border-gold transition-smooth"
                required
              />
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
                  placeholder="Create a strong password"
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
              {/* Password Strength Meter */}
              {password && (
                <div className="space-y-2">
                  <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${passwordStrength.color} transition-all duration-300`}
                      style={{ width: `${passwordStrength.strength}%` }}
                    ></div>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    Password strength: <span className="font-semibold">{passwordStrength.text}</span>
                  </p>
                </div>
              )}
            </div>

            {/* Confirm Password Field */}
            <div className="space-y-2">
              <Label htmlFor="confirmPassword" className="text-primary flex items-center gap-2">
                <Lock className="w-4 h-4" />
                Confirm Password
              </Label>
              <div className="relative">
                <Input
                  id="confirmPassword"
                  type={showConfirmPassword ? "text" : "password"}
                  placeholder="Confirm your password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="pr-10 focus:ring-gold focus:border-gold transition-smooth"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-primary transition-smooth"
                >
                  {showConfirmPassword ? (
                    <EyeOff className="w-5 h-5" />
                  ) : (
                    <Eye className="w-5 h-5" />
                  )}
                </button>
              </div>
              {confirmPassword && password !== confirmPassword && (
                <p className="text-sm text-destructive">Passwords do not match</p>
              )}
            </div>

            {/* Terms Agreement */}
            <div className="flex items-start space-x-2">
              <Checkbox
                id="terms"
                checked={agreeToTerms}
                onCheckedChange={(checked) => setAgreeToTerms(checked as boolean)}
                className="mt-1 border-gold data-[state=checked]:bg-gold data-[state=checked]:border-gold"
              />
              <label htmlFor="terms" className="text-sm text-muted-foreground cursor-pointer">
                I agree to the{" "}
                <span className="text-gold hover:text-gold/80 font-medium">Terms & Conditions</span>{" "}
                and <span className="text-gold hover:text-gold/80 font-medium">Privacy Policy</span>
              </label>
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
                  Creating account...
                </span>
              ) : (
                "Create Account"
              )}
            </Button>
          </form>

          {/* Sign In Link */}
          <div className="mt-6 text-center">
            <p className="text-muted-foreground">
              Already have an account?{" "}
              <Link
                to="/login"
                className="text-gold hover:text-gold/80 font-semibold transition-smooth"
              >
                Sign In
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

export default Signup;
