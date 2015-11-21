#ifndef _NEUTRONTEST_HPP_
#define _NEUTRONTEST_HPP_
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <mysql.h>

#include "global.h"
#include "DbConnect.hpp"

class CNeutronTest
{
    public:
        CNeutronTest();
        ~CNeutronTest();

	int Init(DbConnect* pcDbConnect);
	int TestNetwork();

    private:
	DbConnect* m_pcDbConnect_;
};

#endif
