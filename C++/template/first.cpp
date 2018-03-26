#include <iostream>
#include <assert.h>

using namespace std;

template < class type, int dim >
class Point {
public:
	Point() {}
	Point(type coords[dim]) {
		for (int index = 0; index < dim; index++) {
			_coords[index] = coords[index];
		}
	}

	type& operator[] (int index) {
		assert(index < dim && index >= 0);
		return _coords[index];
	}

	type operator[] (int index) const {
		assert(index < dim && index >= 0);
		return _coords[index];
	}

private:
	type _coords[dim];
};

template <typename T, int size> //size即为非模板类型参数  
//T sum(T& arr[size])
T sum(T(&arr)[size])
{
	T tmp(0);
	for (int i = 0; i < size; ++i)
	{
		tmp += arr[i];
	}
	return tmp;
}

template <typename T>
int cmp(const T &left, const T &right)
{
	return left - right;
}
template <>
int cmp<const char * &>(const char * &p1, const char * &p2)
{
	return strcmp(p1, p2);
}

template<typename T>
class SeqList
{
public:
	SeqList();
	~SeqList();
private:
	int _size;
	int _capacity;
	T* _data;
};
template <typename T>
SeqList <T>::SeqList()
	: _size(0)
	, _capacity(10)
	, _data(new T[_capacity])
{}
template <typename T>
SeqList <T>::~SeqList()
{
	delete[] _data;
}
void test1()
{
	SeqList<int > sl1;
	SeqList<double > sl2;
}


int main()
{
	int arr[5] = { 1,2,3,4,5 };
	cout << sum(arr) << endl; //这里调用时，自动将10传递给size，作为数组元素个数  
	return 0;
}

int main1()
{
	Point<int, 3> p;
	p[2] = 1;
	cout << p[2] << endl;
	return 0;
}