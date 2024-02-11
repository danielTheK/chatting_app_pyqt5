10$$Test1Primes.cpp$$file

	std::stringstream strStream;
	strStream << inFile.rdbuf(); //read the file
	std::string str = strStream.str(); //str holds the content of the file

	return str;
}

std::string vectorToString(const std::vector<int> v)
{
	std::string result = "";
	for (unsigned int i = 0; i < v.size(); i++)
	{
		result += std::to_string(v[i]);
		if (i < v.size() - 1)
			result += ", ";
	}
	return result;
}

bool test1Primes()
{
	bool result = false;

	try
	{
		// Tests Ex11 part 1 - primes

		set_console_color(TEAL);
		cout <<
			"*******************\n" <<
			"Test 1 - Primes	\n" <<
			"*******************\n" << endl;

		set_console_color(WHITE);

		cout <<
			"Calling I_Love_Threads() ... \n" << endl;

		std::streambuf* psbuf, * backup;
		std::stringstream ss;

		backup = std::cout.rdbuf();			// back up cout's streambuf

		psbuf = ss.rdbuf();					// get the string stream streambuf
		std::cout.rdbuf(psbuf);      // assign streambuf to cout

		I_Love_Threads();

		std::cout.rdbuf(backup);     // restore cout's original streambuf

		std::string expected = "I Love Threads\n";
		std::string got = ss.str();
		cout << "Expected: " << expected << endl;
		cout << "Got     : " << got << std::endl;
		if (got != expected)
		{
			set_console_color(RED);
			std::cout << "FAILED: I_Love_Threads() information is not as expected\n" <<
				"Make sure you are printing \"I Love Threads\\n\"\n";
			return false;
			set_console_color(WHITE);
		}

       cout <<
           "\nInitializing empty vector v and calling getPrimes(0, 1000, v)... \n" << endl;

	   std::vector<int> v;
	   getPrimes(0, 1000, v);

	   expected = readFileToString("output1.txt");
       got = vectorToString(v);
       cout << "Expected: " << expected << endl;
       cout << "Got     : " << got << std::endl;
       if (got != expected)
       {
           set_console_color(RED);
           std::cout << "FAILED: getPrimes information is not as expected\n" <<
               "check function getPrime(int, int, std::vector&) \n";
           return false;
           set_console_color(WHITE);
       }

	   cout <<
		   "\nInitializing empty vector v2 and calling getPrimes(0, 1000, v)... \n" << endl;
	   std::vector<int> v2;
	   getPrimes(0, 100000, v2);

	   expected = readFileToString("output2.txt");
	   got = vectorToString(v2);
	   cout << "Expected: " << "9592 prime numbers" << endl;
	   cout << "Got     : " << std::to_string(v2.size()) << " prime numbers" << std::endl;
	   if (got != expected)
	   {
		   set_console_color(RED);
		   std::cout << "FAILED: getPrimes information is not as expected\n" <<
			   "check function getPrime(int, int, std::vector&), \n";
		   return false;
		   set_console_color(WHITE);
	   }

	   cout <<
		   "\nInitializing vector v3 = callGetPrimes(0, 1000)... \n" << endl;
	   std::vector<int> v3;
	   v3 = callGetPrimes(0, 100000);

	   expected = readFileToString("output2.txt");
	   got = vectorToString(v3);
	   cout << "Expected: " << "9592 prime numbers" << endl;
	   cout << "Got     : " << std::to_string(v3.size()) << " prime numbers" << std::endl;
	   if (got != expected)
	   {
		   set_console_color(RED);
		   std::cout << "FAILED: callGetPrimes information is not as expected\n" <<
			   "check function callGetPrimes(int, int) \n";
		   return false;
		   set_console_color(WHITE);
	   }

	}
	catch (...)
	{
		set_console_color(RED);
		std::cerr << "Test crashed" << endl;
		std::cout << "FAILED: The program crashed, check the following things:\n" <<
			"1. Did you delete a pointer twice?\n2. Did you accesse index out of bounds?\n" <<
			"3. Did you remember to initialize the lists before using them?\n" <<
			"4. Did you remember to call join() or detach() when using threads?\n";
		return false;
	}

	set_console_color(LIGHT_GREEN);
	std::cout << "\n########## Primes - TEST Passed!!! ##########\n\n";
	set_console_color(WHITE);

	return true;

}

int main()
{
	set_console_color(LIGHT_YELLOW);
	std::cout <<
		"###########################\n" <<
		"Exercise 101 - Threads\n" <<
		"Test - Primes\n" << 
		"###########################\n" << std::endl;
	set_console_color(WHITE);

	bool testResult = test1Primes();

	if (testResult)
	{
		set_console_color(GREEN);
		std::cout << "\n########## Ex11 Tests Passed!!! ##########" << "\n\n";
		set_console_color(WHITE);
	}
	else
	{
		set_console_color(RED);
		std::cout << "\n########## TEST Failed :( ##########\n";
		set_console_color(WHITE);
	}

	return 0;
}