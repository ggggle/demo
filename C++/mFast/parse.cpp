#include <iostream>
#include <string>
#include <fstream>
#include <mfast.h>
#include <mfast/coder/fast_decoder.h>
#include <mfast/json/json.h>
#include <mfast/xml_parser/dynamic_templates_description.h>

using std::string;
using std::ostringstream;
using std::cout;
using std::endl;

using mfast::templates_description;
using mfast::dynamic_templates_description;
using mfast::fast_decoder;
using mfast::message_cref;
using mfast::ascii_string_cref;
using mfast::json::encode;

static const char hex_dict[] = {0x0, 0x1, 0x2, 0x3, 0x4, 0x5, 0x6, 0x7, 0x8, 0x9, 0xa, 0xb, 0xc, 0xd, 0xe, 0xf};

int main() {
	string fast_template, fast_message;
	std::fstream template_file("template.xml", std::ios::in);
	if (template_file)
	{
		template_file.seekg(0, std::ios::end);
		size_t len = (size_t) template_file.tellg();
		if (len>0)
		{
			char* tmp = new char[len];
			template_file.seekg(0, std::ios::beg);
			template_file.read(tmp, len);
			fast_template.assign(tmp, len);
			delete []tmp;
		}
		else
		{
			cout<<"template.xml length error"<<endl;
			template_file.close();
			return 0;
		}
		template_file.close();
	}
	else
	{
		cout<<"template.xml not exist"<<endl;
		return 0;
	}
	std::fstream message_file("fast_message.txt", std::ios::in);
	std::fstream out("out.dat", std::ios::out|std::ios::binary);
	if (message_file)
	{
		message_file.seekg(0, std::ios::end);
		size_t len = (size_t) message_file.tellg();
		if (len>0)
		{
			char* tmp = new char[len];
			char* hex = new char[len];
			message_file.seekg(0, std::ios::beg);
			message_file.read(tmp, len);
			for (size_t i=0;i<len;i+=2)
			{
				int high,low;
				if (tmp[i]>'=')
				{
					high = tmp[i] - 55;
				}
				else
				{
					high = tmp[i] - 48;
				}
				if (tmp[i+1]>'=')
				{
					low = tmp[i+1] - 55;
				}
				else
				{
					low = tmp[i+1] - 48;
				}
				hex[i/2] = (hex_dict[high]<<4) + hex_dict[low];
			}
			fast_message.assign(hex, len/2);
			delete []hex;
			delete []tmp;
		}
		else
		{
			cout<<"fast_message.txt length error"<<endl;
			message_file.close();
			return 0;
		}
		message_file.close();
	}
	else
	{
		cout<<"fast_message.txt not exist"<<endl;
		return 0;
	}
  dynamic_templates_description description(fast_template);

  const templates_description* descriptions[] = {&description};

  fast_decoder decoder;
  decoder.include(descriptions);
  out<<fast_message;
  const char* start = fast_message.c_str();
  const char* end = start + fast_message.length();
  
  message_cref msg = decoder.decode(start, end, false);

  cout << "Template id: " << msg.id() << endl;
  cout << "Template name: " << msg.name() << endl;
  cout << endl;

  cout << "[0]Encoding message to JSON:" << endl;

  ostringstream json_message;
  bool result = encode(json_message, msg, 0);
  if (result) 
  {
	  cout << "Success: " <<endl<< json_message.str() << endl<<endl;
	  for(size_t i=1;start!=end;++i)
	  {
		  message_cref msg = decoder.decode(start, end, false);
		  cout <<"["<<i<<"]"<< "Encoding message to JSON:" << endl;
		  ostringstream json_message;
		  result = encode(json_message, msg, 0);
		  if (result)
		  {
			  cout << "Success: " <<endl<< json_message.str() << endl<<endl;
		  }  
	  }
  }
  return 0;
}
