//cex_vbr_vlanmap.h
//
//REF : coordinator/modules/odcdriver/include/odc_vbr_vlanmap.hh

#ifndef _CEX_VBR_VLANMAP_HH
#define _CEX_VBR_VLANMAP_HH

#include <unc/upll_ipc_enum.h>
#include <unc/pfcdriver_ipc_enum.h>
#include <string>
#include <vector>
#include <sstream>
#include <unc_base/h> //define UncRespCode
#include "cex_common.h"
#include "cex_vtn.h"

class OdcVbrVlanMapCommand {
 public:
  explicit OdcVbrVlanMapCommand(unc::restjson::ConfFileValues_t conf_values);
  ~OdcVbrVlanMapCommand();

  /**
   * @brief                      - Forms VBR_VLANMAP command and send it to
   *                               restclient interface to create vbrvlanmap
   * @param[in] key              - key structure of VBR_VLANMAP
   * @param[in] val              - value structure of VBR_VLANMAP
   * @param[in] conn             - Controller pointer
   * @retval UncRespCode         - returns DRVAPI_RESPONSE SUCCESS on creation
   *                             - of VBR_VLANMAP successfully
   *                               /returns UNC_DRV_RC_ERR_GENERIC on failure
   */
  UncRespCode create_cmd(key_vlan_map_t& key,
                         pfcdrv_val_vlan_map_t& val,
                         unc::driver::controller *conn);

  /**
   * @brief                      - Forms VBR_VLANMAP command and send it to
   *                               restclient interface to update vbrvlanmap
   * @param[in] key              - key structure of VBR_VLANMAP
   * @param[in] val              - Old value structure of VBR_VLANMAP
   * @param[in] val              - New value structure of VBR_VLANMAP
   * @param[in] conn             - Controller pointer
   * @retval UncRespCode         - returns UNC_RC_SUCCESS on
   *                             - updation of VBR_VLANMAP successfully
   *                             - returns UNC_DRV_RC_ERR_GENERIC on failure
   */
  UncRespCode update_cmd(key_vlan_map_t& key,
                         pfcdrv_val_vlan_map_t& val_old,
                         pfcdrv_val_vlan_map_t& val_new,
                         unc::driver::controller *conn);

  /**
   * @brief                      - Deletes VBR_VLANMAP and send it to restclient
   *                               interface to delete vbrvlanmap
   * @param[in] key              - key structure of VBR_VLANMAP
   * @param[in] val              - value structure of VBR_VLANMAP
   * @param[in] conn             - Controller pointer
   * @return UncRespCode         - returns UNC_RC_SUCCESS on deletion of
   *                             - VBRIf successfully /returns
   *                             - UNC_DRV_RC_ERR_GENERIC on failure
   */
  UncRespCode delete_cmd(key_vlan_map_t& key,
                         pfcdrv_val_vlan_map_t& val,
                         unc::driver::controller *conn);

  /**
   * @brief                      - get all the vbrvlanmaps inside particular vbr
   * @param[in] parent_key       - parent key type pointer
   * @param[in] ctr              - controller pointer
   * @param[out] cfgnode_vector  - config node vector
   * @return UncRespCode         - returns UNC_RC_SUCCESS on success
   *                              /returns UNC_DRV_RC_ERR_GENERIC on failure
   */
  UncRespCode get_vbrvlanmap_list(
      void* parent_key,
      unc::driver::controller* ctr,
      std::vector< unc::vtndrvcache::ConfigNode *> &cfgnode_vector);
};
#endif
