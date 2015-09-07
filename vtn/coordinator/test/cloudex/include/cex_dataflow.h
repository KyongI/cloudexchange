//cex_dataflow.h
//
//REF : ./coordinator/modules/odcdriver/include/odc_dataflow.hh

#ifndef _CEX_DATAFLOW_HH_
#define _CEX_DATAFLOW_HH_

#include <unc/pfcdriver_ipc_enum.h>
#include <string>
#include <vector>
#include <sstream>
#include <unc_base/h> //define UncRespCode
#include "cex_common.h"
#include "cex_vtn.h"

#define VAL_MAC_ADDR_SIZE 6

class DataFlowCommand {
 public:
  explicit DataFlowCommand(ConfFileValues_t conf_values);

  /**
   * @brief Default Destructor
   */
  ~OdcDataFlowCommand();

  UncRespCode read_cmd(unc::driver::controller *ctr,
                       unc::vtnreadutil::driver_read_util*);
};
#endif
