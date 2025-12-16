import GetStartedButton from "@/components/ui/button/GetStartedButton";

export default function Home() {
  return (
    <div className="min-h-screen bg-white flex flex-col justify-center items-center px-4">
      <div className="max-w-2xl w-full text-center space-y-8">
        {/* Logo/Brand */}
        <div className="space-y-4">
          <h1 className="text-6xl font-bold text-purple-600">
            SentiCore
          </h1>
          <p className="text-xl text-gray-600 max-w-md mx-auto">
            Your intelligent conversation companion powered by SNN
          </p>
        </div>



        {/* CTA Button */}
        <div className="pt-4">
          <GetStartedButton />
        </div>
      </div>
    </div>
  );
}